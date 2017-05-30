import csv
import os
from datetime import datetime, date

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from django.views.generic import View

from myrobogals.decorators import staff_or_404
from myrobogals.rgprofile.models import User
from myrobogals.rgprofile.views.profile_chapter import exportusers
from myrobogals.rgteaching.models import SchoolVisit, SchoolVisitStats, EventAttendee, School


class CSVWorkshopsUploadForm(forms.Form):
    csvfile = forms.FileField(widget=forms.FileInput(attrs={'accept': '.csv'}))


def check_file_extension(value):
    if not value.name.endswith('.csv'):
        raise ValidationError('Please upload a .csv file')


class ReviewUploadForm(forms.Form):
    checked_upload = forms.BooleanField()


def download(request):
    """
    Allows the user to download the mass import workshop sample csv file
    """
    g = request.GET.get('doc', None)
    fp = ''

    if g is not None:
        # Template Spreadsheet
        if g == 'sample':
            fp = os.path.join(settings.MEDIA_ROOT, 'sample/workshopuploadsample.csv')

        # Schools List
        elif g == 'schoollist':
            schools_list = School.objects.filter(chapter=request.user.chapter)

            filename = request.user.chapter.myrobogals_url + '-schools-' + str(date.today()) + '.csv'
            fp = 'tmp/' + filename
            with open(fp, 'wb') as csvfile:
                w = csv.writer(csvfile, delimiter=',')

                w.writerow(['School ID', 'School'])
                for s in schools_list:
                    w.writerow([str(s.id), s.name.encode('ascii', 'ignore')])

        elif g == 'userlist':
            return exportusers(request, request.user.chapter.myrobogals_url)

        if os.path.exists(fp):
            with open(fp, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(fp)
                return response

    raise Http404


class ImportWorkshopView(View):
    """
    Mass importing workshop statistics using upload form and converts .CSV file into database entries 
    """

    form_class = CSVWorkshopsUploadForm

    @method_decorator(login_required)
    @method_decorator(staff_or_404)
    def post(self, request):
        chapter = request.user.chapter
        step = request.POST['step']

        if step == '1':
            return self.step_one(request, chapter)
        elif step == '2':
            return self.step_two(request, chapter)
        else:
            messages.error(request, 'An error occurred, please try again.')
            return HttpResponseRedirect(reverse('teaching:home'))

    @method_decorator(login_required)
    @method_decorator(staff_or_404)
    def get(self, request):
        return render(request, 'import_workshops_1.html',
                      {'chapter': request.user.chapter, 'form': self.form_class})

    def step_one(self, request, chapter):
        # User has uploaded form, time for them to review the file
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['csvfile']

            # Writing file data to local csv file
            tmppath = 'tmp/' + chapter.myrobogals_url + request.user.username + '.csv'
            with open(tmppath, 'w') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Opens file to read as text file and lines are terminated by any convention
            f = open(tmppath, 'rU')
            filerows = csv.reader(f)

            (workshops_list, workshops_imported, err_msg) = self.import_workshop_csv(request, filerows, False)

            if workshops_imported is None:
                # Rerendering possible error messages
                if err_msg:
                    err_str = ''
                    for key, val in err_msg.iteritems():
                        err_str += val + '<br>'
                    messages.error(request, err_str)

                return HttpResponseRedirect(reverse('teaching:home'))

            form_review = ReviewUploadForm()
            return render(request, 'import_workshops_2.html',
                          {'workshops_list': workshops_list, 'workshop_imported': workshops_imported,
                           'err_msg': err_msg, 'form_review': form_review, 'tmppath': tmppath})

    def step_two(self, request, chapter):
        # Extract all the information from the file and save it to database
        if 'tmppath' not in request.POST:
            messages.error(request, 'An error has occurred, try reimporting workshop stats')
            return HttpResponseRedirect('/chapters/' + chapter.myrobogals_url + '/edit/users/import/')

        form_review = ReviewUploadForm(request.POST)
        if form_review.is_valid():
            # Opens file and import workshops
            tmppath = request.POST['tmppath'].replace('\\\\', '\\')

            if os.path.exists(tmppath):
                fp = open(tmppath, 'rU')
                filerows = csv.reader(fp)
            else:
                messages.error(request, 'An error occurred, please reupload your document')
                return HttpResponseRedirect(reverse('teaching:import_workshops'))

            (workshops_list, workshops_imported, err_msg) = self.import_workshop_csv(request, filerows, True)

            # Display success messages
            if workshops_imported:
                messages.success(request, 'Imported %d workshops to %s' % (workshops_imported, chapter))

            # Display error messages
            if err_msg:
                err_str = ''
                for key, val in err_msg.iteritems():
                    err_str += val + '<br>'

                messages.error(request, err_str)

            # Removing uploaded file
            try:
                os.remove(tmppath)
            except OSError:
                pass

            return HttpResponseRedirect(reverse('teaching:home'))
        else:
            # When the user has not reviewed the upload form (clicked the checkbox)
            tmppath = request.POST['tmppath'].replace('\\\\', '\\')
            fp = open(tmppath, 'rU')
            filerows = csv.reader(fp)

            (workshops_list, workshops_imported, err_msg) = self.import_workshop_csv(request, filerows, False)

            return render(request, 'import_workshops_2.html',
                          {'workshops_list': workshops_list, 'workshop_imported': workshops_imported,
                           'err_msg': err_msg, 'form_review': form_review, 'tmppath': tmppath})

    @staticmethod
    def import_workshop_csv(request, filerows, save):
        columns = None
        workshops_imported = 0
        workshop_list = []
        err_msg = {}
        row_idx = 0

        # Find the indices of fields
        for row in filerows:
            if any(row):
                row_idx += 1
                if columns is None:
                    columns = row

                    # Check to see there are an appropriate number of columns in the header
                    if len(columns) < 20:
                        err_msg.update({str(row_idx): 'You are missing columns in your .csv table. Please correct the error and try again.'})
                        workshops_imported = None
                        return workshop_list, workshops_imported, err_msg

                    continue

                school_visit = SchoolVisit()
                stats = SchoolVisitStats()

                school_visit.chapter = request.user.chapter
                school_visit.creator = request.user
                school_visit.created_method = 2

                i = 0
                date = ''
                attendees_list = []
                attendee_errors = {}
                data_filled_correctly = False

                for col in row:
                    colname = columns[i]
                    i += 1

                    if i > 19: i = 19

                    if 'Attendees' in colname:
                        if i != 19:
                            err_msg.update({str(row_idx): 'There was an incorrect number of items in this row, please check your columns from template again'})
                            break

                        # ASSUMPTION: The remaining columns in a row are all volunteer usernames
                        data_filled_correctly = True
                        attendee = EventAttendee()

                        try:
                            # Empty attendee field
                            if not col:
                                continue

                            # Try to find in the user exists
                            u = User.objects.get(username__exact=col)
                        except ObjectDoesNotExist:
                            try:
                                attendee_errors[str(row_idx)] += '<br>Could not find %s and has not been added to the workshop' % col
                            except KeyError:
                                attendee_errors.update({str(row_idx): 'Could not find %s and has not been added to the workshop' % col})

                            continue

                        attendee.user = u
                        attendee.actual_status = 1
                        attendee.rsvp_status = 0
                        attendees_list.append(attendee)
                    else:
                        if colname == 'School ID':
                            try:
                                school_visit.school = School.objects.get(pk=sint(col), chapter=request.user.chapter)
                            except ObjectDoesNotExist:
                                err_msg.update({str(row_idx): "That school ID does not exist in your schools database, please check again from your schools list. If they don't exist, add them in the Schools tab and try again"})
                                break

                        elif colname == 'Visit Date':
                            # Check for correct format
                            try:
                                date = datetime.strptime(col, '%d/%m/%Y')
                            except ValueError:
                                err_msg.update({str(row_idx): 'The date format specified (%s) is not in the correct format' % col})
                                break

                            # Check if user enters an event that's set in the future
                            if make_aware(date, timezone=request.user.chapter.tz_obj()) > datetime.now(tz=request.user.chapter.tz_obj()):
                                err_msg.update({str(row_idx): 'This event has not occurred yet and therefore cannot be entered in'})
                                break
                        elif colname == 'Start Time':
                            # Check for correct format
                            try:
                                t = datetime.strptime(col, '%H:%M:%S').time()
                            except ValueError:
                                try:
                                    # Try another format cause excel -_-
                                    t = datetime.strptime(col, '%H:%M').time()
                                except ValueError:
                                    err_msg.update({str(row_idx): 'The start time specified (%s) is not in the correct format' % col})
                                    break

                            school_visit.visit_start = make_aware(datetime.combine(date, t), timezone=request.user.chapter.tz_obj())
                        elif colname == 'End Time':
                            # Check for correct format
                            try:
                                t = datetime.strptime(col, '%H:%M:%S').time()
                            except ValueError:
                                try:
                                    # Try another format cause excel -_-
                                    t = datetime.strptime(col, '%H:%M').time()
                                except ValueError:
                                    err_msg.update({str(row_idx): 'The end time specified (%s) is not in the correct format' % col})
                                    break

                            school_visit.visit_end = make_aware(datetime.combine(date, t), timezone=request.user.chapter.tz_obj())

                            if school_visit.visit_end < school_visit.visit_start:
                                err_msg.update({str(row_idx): 'The end time is earlier than start time'})
                                break

                        elif colname == 'Location':
                            if col == '':
                                err_msg.update({str(row_idx): 'You must specify a location for this visit'})
                                break

                            school_visit.location = col
                        elif colname == 'Visit Type ID':
                            if sint(col) < 0 or sint(col) > 7:
                                stats.visit_type = 0
                            else:
                                stats.visit_type = sint(col)
                        elif colname == 'Primary Girls First':
                            stats.primary_girls_first = sint(col)
                        elif colname == 'Primary Girls Repeat':
                            stats.primary_girls_repeat = sint(col)
                        elif colname == 'Primary Boys First':
                            stats.primary_boys_first = sint(col)
                        elif colname == 'Primary Boys Repeat':
                            stats.primary_boys_repeat = sint(col)
                        elif colname == 'High Girls First':
                            stats.high_girls_first = sint(col)
                        elif colname == 'High Girls Repeat':
                            stats.high_girls_repeat = sint(col)
                        elif colname == 'High Boys First':
                            stats.high_boys_first = sint(col)
                        elif colname == 'High Boys Repeat':
                            stats.high_boys_repeat = sint(col)
                        elif colname == 'Other Girls First':
                            stats.other_girls_first = sint(col)
                        elif colname == 'Other Girls Repeat':
                            stats.other_girls_repeat = sint(col)
                        elif colname == 'Other Boys First':
                            stats.other_boys_first = sint(col)
                        elif colname == 'Other Boys Repeat':
                            stats.other_boys_repeat = sint(col)
                        elif colname == 'Notes':
                            stats.notes = col
                        else:
                            err_msg.update({str(row_idx): "Column not recognised, use the column names provided in the template and reupload your file."})
                            return workshop_list, workshops_imported, err_msg

                # Only check for existence and save when data is filled correctly
                if data_filled_correctly:
                    # Perform saves to database
                    d_start = datetime.replace(school_visit.visit_start, microsecond=0, tzinfo=None).__format__('%d/%m/%y %H:%M')
                    d_end = datetime.replace(school_visit.visit_end, microsecond=0, tzinfo=None).time().__format__('%H:%M')

                    try:
                        s = SchoolVisit.objects.get(
                            visit_start=school_visit.visit_start,
                            visit_end=school_visit.visit_end,
                            school=school_visit.school
                        )

                        err_msg.update({str(row_idx): ' Visit to %s on %s-%s already exists in the database' % (school_visit.school.name, d_start, d_end)})
                        continue
                    except ObjectDoesNotExist:
                        w = {'text': {str(row_idx): 'Adding visit to %s on %s-%s' % (school_visit.school.name, d_start, d_end)}, 'attendees': attendees_list}
                        workshop_list.append(w)

                        if save:
                            school_visit.status = 1
                            school_visit.save()
                            stats.visit = school_visit
                            stats.save()

                            # Save the stats of all attendees
                            for attendee in attendees_list:
                                attendee.event = school_visit
                                attendee.save()

                        err_msg.update(attendee_errors)
                        workshops_imported += 1

        return workshop_list, workshops_imported, err_msg


def sint(val):
    """
    Ensures that numbers are greater than 0, otherwise, set them 0
    """
    try:
        a = int(val)
        return a if a > 0 else 0
    except ValueError:
        return 0
