/*!

myRobogals
R2D2

James Li
20140705

*/

var myRG = myRG || {};

(function(myRG){
    // Start up
    
    // CSRF and AJAX
    /*! https://docs.djangoproject.com/en/1.6/ref/contrib/csrf/#ajax */
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    
    
    
    
    
    // Useful functions
    
    // Test nested obj properties
    /*! http://stackoverflow.com/a/4676258 */
    function testPropertyExists(a,e){for(var c=e.split("."),b=0,f=c.length;b<f;b++){var d=c[b];if(null!==a&&"object"===typeof a&&d in a)a=a[d];else return!1}return!0};

    
    
    
    
    
    
    // Stamp store obj
    function modelStore(){
        this.store = {};
        
        this.set = function (key, value){
            this.store[key] = value;
            return this.get(key);
        };
        
        this.get = function (key){
            return this.store[key];
        };
        
        this.reset = function (key){
            this.store = {};
        };
    };

    // Various bits
    myRG.globalStore = new modelStore();
    myRG.appStore = new modelStore();
    myRG.userStore = new modelStore();
    myRG.settings = new modelStore();
    myRG.jq = {};
    myRG.functions = {};
        
    // Shorthands
    var s = myRG.settings;
    var jq = myRG.jq;
    var g = myRG.globalStore;
    var a = myRG.appStore;
    var u = myRG.userStore;
    var f = myRG.functions;
        
        
        
        
        
        
        
        
    // Set settings
    s.set("INIT_STARTUP_LATENCY_ALLOWANCE", 500);   // ms
    
    s.set("TRAY_MIN_TIME", 3500);                   // ms
    s.set("TRAY_WAIT_BEFORE_SCROLL", 1500);         // ms
    s.set("TRAY_WAIT_AFTER_SCROLL", 1500);          // ms
    s.set("TRAY_SCROLL_SPEED", 12);                 // ms/px (lower = faster)
    s.set("TRAY_TRANSITION_SPEED", 500);            // ms/px (lower = faster)
    

    
    s.set("API_ROOT_URL", "/api/1.0/");
    
    
    
    
    
    
    
    
    // Core functions
    
    f.getAPIURL = function(endpoint) {
        return s.get("API_ROOT_URL") + endpoint.replace(/^\/|\/$/g, '') + ".json";
    }

    f.fetchWhoAmI = function(){
        return $.post(f.getAPIURL("/self/whoami"), {});
    }
    
    
    
    
    
    
    // Start prefetching before DOM ready
    u.set("WHOAMI_XHR",f.fetchWhoAmI());
    
    
    
    
    
    
    
    // DOM ready
    $(function(){
        jq.body = $("body");
        jq.menu = $("#menu");
        jq.header = $("#header");
        jq.tray = $("#tray");
        jq.profile = jq.menu.find(".profile");
        jq.menuUnderlay = $("#menu-underlay");
        
        g.set("GRAVATAR_TEMPLATE", jq.profile.find(".image").data("image"));
        
        
        
        // Functions
        
        f.throwError = function(error) {
            f.setTray('<b><i class="fa fa-frown-o"></i> Error: </b>'+error.message,"fail",false);
            
            throw error;
        }
        
        
        
        
        
        
        f.setMenuTabbability = function (){
            // if (jq.body.hasClass("menu-open")) {
                // jq.menu.find("*[tabindex]").attr("tabindex","0");
            // } else {
                // jq.menu.find("*[tabindex]").attr("tabindex","-1");
            // }
        }
        
        f.clearTrayActivity = function () {
            jq.tray.stop();
            
            if (g.get("TRAY_CLOSE_TIMER")) {
                clearTimeout(g.get("TRAY_CLOSE_TIMER"));
            }
        }
        
        f.openTray = function (closable, time) {
            f.clearTrayActivity();
            jq.body.addClass("tray-open");
            
            var diff = jq.tray.children(".text").outerWidth() - jq.tray.width();
            
            var scrollTime = diff * s.get("TRAY_SCROLL_SPEED");
            var trayOpenTime = s.get("TRAY_WAIT_BEFORE_SCROLL") + scrollTime + s.get("TRAY_WAIT_AFTER_SCROLL");
            
            if (trayOpenTime < time) {
                trayOpenTime = time;
            }
            
            if (diff > 0) {
                jq.tray.delay(s.get("TRAY_WAIT_BEFORE_SCROLL")).animate({
                    scrollLeft: diff
                }, scrollTime, "linear");
            }
            
            if (closable) {
                return g.set("TRAY_CLOSE_TIMER", setTimeout(f.closeTray, trayOpenTime));
            } else {
                return g.set("TRAY_CLOSE_TIMER", -1);
            }
        }
        
        f.setTray = function (html, className, closable, time){
            closable = typeof closable !== 'undefined' ? closable : true;
            className = className || "";
            time = time || s.get("TRAY_MIN_TIME");
            
            clearTimeout(g.get("TRAY_CLASS_REMOVE_TIMER"));
            jq.tray.removeClass();
            jq.tray.addClass(className);
            
            jq.tray.scrollLeft(0);
            jq.tray.children(".text").html(html);
            
            return f.openTray(closable, time);
        }
        
        f.closeTray = function (){
            f.clearTrayActivity();
            jq.body.removeClass("tray-open");
            
            g.set("TRAY_CLASS_REMOVE_TIMER", setTimeout(function(){
                jq.tray.removeClass();
            }), s.get("TRAY_TRANSITION_SPEED")+33)
        }
        
        
        
        
        
        
        f.toggleMenu = function (){
            jq.body.toggleClass("menu-open");
            f.setMenuTabbability();
        }
        
        f.toggleUserMenu = function (){
            jq.body.toggleClass("user-open");
        }
        
        
        
        
        
        f.updateUser = function(whoami) {
            if (whoami) {
                u.set("ID",whoami.user.id);
                f.loadProfileImage(whoami.user.data.gravatar_hash);
                f.loadProfileName(whoami.user.data.display_name);
                f.loadProfileRole("");
                f.loadProfileGroup("");
            } else {
                u.set("ID",0);
                f.loadProfileImage(0);
                f.loadProfileName("Anonymous User");
                f.loadProfileRole("");
                f.loadProfileGroup("");
            }
        }
        
        f.loadProfileImage = function (gravatarHash){
            jq.profile.find(".image").css("background-image","url("+ g.get("GRAVATAR_TEMPLATE").replace("{gravatar_hash}",gravatarHash) +")");
        }
        
        f.loadProfileName = function (name){
            jq.profile.find(".name").text(name);
        }
        
        f.loadProfileRole = function (role){
            jq.profile.find(".role").text(role);
        }
        
        f.loadProfileGroup = function (group){
            jq.profile.find(".group").text(group);
        }
        
        
        
        
        
        // Events
        
        jq.tray.click(function(){
            if (g.get("TRAY_CLOSE_TIMER") != -1){
                f.closeTray();
            }
        });
        
        jq.header.click(function(){
            f.toggleMenu();
        })
        
        jq.menuUnderlay.click(function(){
            f.toggleMenu();
        })
        
        jq.profile.click(function(e){
            f.toggleUserMenu();
            e.preventDefault();
        })
        
       
        
        
        
        // Start!
        
        // If old IE (lt. IE 9) then stop
        if ($("#ie-old-warning").length){
            jq.body.children(":not(#ie-old-warning)").hide();
            return;
        }
        
        
        // Grab user info
        
        // Add a little bit of latency allowance so that the loading message
        // doesn't flicker for those on high speed connections
        // --- disabled for now
        
        var initLoadMessageTimer = setTimeout(function(){
                                                f.setTray("Loading...","indeterminate",false);
                                                //}, s.get("INIT_STARTUP_LATENCY_ALLOWANCE"));
                                                }, 0);
        
        // XHR is done before DOM ready. See above.
        
        u.get("WHOAMI_XHR").always(function(){
            clearTimeout(initLoadMessageTimer);
        });
        
        u.get("WHOAMI_XHR").done(function(data){
            f.updateUser(data);
            f.closeTray();
            jq.body.addClass("loaded menu-enabled header-enabled stage-enabled");
        });
        
        u.get("WHOAMI_XHR").fail(function(jqXHR){                
                if (jqXHR.status == 401){
                    f.updateUser();
                    f.closeTray();
                    jq.body.addClass("loaded menu-enabled header-enabled stage-enabled");
                } else {
                    f.throwError({
                                    name: 'PROFILE_UNAVAILABLE',
                                    message: 'Profile unavailable. Reload page to try again.'
                                });
                }
        });
        
        
    });
})(myRG);