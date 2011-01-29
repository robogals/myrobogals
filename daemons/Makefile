CC=gcc
CFLAGS=-c -I/usr/include -DDEBUG
LDFLAGS=-L/usr/lib -lcurl -lmysqlclient -lm -lz

all: rgsmsd

rgsmsd: smsglobal.o nudge_sql.o rgsmsd.o pidfile.o eventlog.o
	${CC} -o rgsmsd smsglobal.o nudge_sql.o rgsmsd.o pidfile.o eventlog.o ${LDFLAGS}

rgsmsd.o: rgsmsd.c rgsmsd.h nudge_sql.h smsglobal.h
	${CC} ${CFLAGS} -o rgsmsd.o rgsmsd.c

nudge_sql.o: nudge_sql.c nudge_sql.h
	${CC} ${CFLAGS} -o nudge_sql.o nudge_sql.c

smsglobal.o: smsglobal.c smsglobal.h
	${CC} ${CFLAGS} -o smsglobal.o smsglobal.c

pidfile.o: pidfile.c pidfile.h
	${CC} ${CFLAGS} -o pidfile.o pidfile.c

eventlog.o: eventlog.c eventlog.h
	${CC} ${CFLAGS} -o eventlog.o eventlog.c

.PHONY: clean clobber

clean:
	rm -f *.o

clobber: clean
	rm -f rgsmsd
