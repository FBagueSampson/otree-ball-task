 /* ==== Hard Timer Script ==== */
    let customTimerEle = document.getElementById('CountdownClock');

    function addZero(obj) {
        if (obj < 10) {obj = "0" + obj}
        return obj;
    }

    function makeitBaseSixty(remainingTime) {
        var hoursLeft = Math.floor(remainingTime/3600);
        var minutesLeft = Math.floor((remainingTime - hoursLeft*3600)/60);
        var secondsLeft = remainingTime - Math.floor(remainingTime/60)*60;
        let h = addZero(hoursLeft);
        let m = addZero(minutesLeft);
        let s = addZero(secondsLeft);
        return {h, m, s};
    }

    document.addEventListener("DOMContentLoaded", function (event) {
        $('.otree-timer__time-left').on('update.countdown', function (event) {
            let displayClock = makeitBaseSixty(event.offset.totalSeconds);
            if (displayClock.h < 1) {
                customTimerEle.innerHTML = displayClock.m + ":" + displayClock.s;
            } else {
                customTimerEle.innerHTML = displayClock.h + ":" + displayClock.m + ":" + displayClock.s;
            }
        });
    });
