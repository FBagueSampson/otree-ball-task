


/* ========== UPDATE DISPLAY VALUES FOR PARTICIPANTS ========== */
    const bucket01payoff = document.querySelectorAll('.bucket_01_payoff');
    const bucket02payoff = document.querySelectorAll('.bucket_02_payoff');
    const remainingBalls = document.getElementById('balls_remaining');
    const totalEarnings = document.querySelectorAll('#totalEarnings');

    var bucketPayoffs_01, bucketPayoffs_02, nBallsLeft, totalPayoff;

    function set_display(bucketPayoffs_01, bucketPayoffs_02, nBallsLeft, totalPayoff) {
        bucket01payoff.forEach(ele => { 
            ele.innerText = makeItHumanReadable(bucketPayoffs_01); 
        }); 
        bucket02payoff.forEach(ele => { 
            ele.innerText = makeItHumanReadable(bucketPayoffs_02); 
        }); 
        remainingBalls.innerText = nBallsLeft;
        totalEarnings.innerText = makeItHumanReadable(totalPayoff);
    }


/* ========== ENSURE DISPLAY VALUES ARE MEANINGFUL WHEN RENDERED BY JAVASCRIPT ========== */
    function makeItHumanReadable(obj) {
        obj = Number(obj);
        if (obj % 1 != 0) {
            obj = obj.toFixed(2);
        }
        return obj;
    }


/*  ========== BALL DRAGGING AND DROPPING SCRIPT ========== */

 /* ~~~~ PRELIMINARY JUNK FOR TRACKING THE BALL AND SETTING UP THE BUCKETS AS TARGETS ~~~~ */
    const ballContainer = document.getElementById('ballbag');

    /* draggable element: ball */
    const item = document.querySelector('.ball'); // finds html elements of class="ball"

    /* event listeners for the ball */
    item.addEventListener('dragstart', dragStart); // listens for start of dragging ball
    item.addEventListener('dragend', dragStop); // listens for end of dragging ball, wherever that happens

    /* functions for ball events */
    function dragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.id); // grabs the id of the ball, "draggable_ball"
        e.target.classList.add('while-dragging'); // adds the class "while-dragging" to the element on the event
    }

    function dragStop(e) {
        e.target.classList.remove('while-dragging'); // removes the class "while-dragging" to the element on the event
    }

    /* drop targets: buckets */
    const buckets = document.querySelectorAll('.droppable'); // finds html elements of class="droppable"

    /* event listeners for the buckets : applies each event listener to all buckets on page */
    buckets.forEach(buckets => {
        buckets.addEventListener('dragenter', dragEnter)
        buckets.addEventListener('dragover', dragOver);
        buckets.addEventListener('dragleave', dragLeave);
        buckets.addEventListener('drop', dropOn);
    });

    /* functions for bucket events */
    function dragEnter(e) {
        e.preventDefault();
        e.target.classList.add('drag-over'); // adds the class "drag-over" to the element on the event
    }

    function dragOver(e) {
        e.preventDefault();
        e.target.classList.add('drag-over'); // adds the class "drag-over" to the element on the event
    }

    function dragLeave(e) {
        e.preventDefault();
        e.target.classList.remove('drag-over'); // removes the class "drag-over" to the element on the event
    }

    var targetValue, chosenBucket; //
    var animateInterval = null; // new for ball-drop

 /* ~~~~ DETERMINES WHICH BUCKET IS SENT TO SERVER: LIVE SEND!! BEGINS COUNT-DOWN FOR LIVE-RECEIVE ~~~~ */
    /* functions for drop event -- happens on the buckets */
    function dropOn(e) {
        e.preventDefault();
        e.target.classList.remove('drag-over'); // removes the class "drag-over" to the element on the event

    // capture choice of bucket and send to server (alllows choice of bucket to be robust to placing ball on the binned balls)
        if (e.target.id == "Bucket02" || e.target.classList.contains("binis02") ) {
            targetValue = 'bucket_02';
            chosenBucket = document.getElementById('Bucket02');
            console.log('on drop ' + targetValue);
        } else if (e.target.id == "Bucket01" || e.target.classList.contains("binis01") ) {
            targetValue = 'bucket_01';
            chosenBucket = document.getElementById('Bucket01');
        }
        
        forminputs.bucket.value = targetValue; // set the value of the form before submitting
        // liveSend({'decision': String(targetValue)}) // sends player choice to server
        
    // get the draggable element
        const id = e.dataTransfer.getData('text/plain'); // returns the id of the ball, "draggable_ball"
        const draggable = document.getElementById(id); // grabs the <div> element with id="id"

    // attach the ball to the drop target
        chosenBucket.appendChild(draggable); // chosenBucket.appendChild(draggable);

    // return display color of the ball to the original pre-dragged style
        draggable.classList.remove('while-dragging');

 /* ~~~~ END of MAIN ball action ~~~~ */


 /* ~~~~ FORM SUBMISSION AND BALL DROP EVENT START ~~~~ */
    // for ball-drop event below. want it delayed? change that 0 to something else
        setTimeout(() => {
            draggable.style.position = 'absolute'; // required for javascript ball-falling
            ballDrop(draggable);
        }, 0);


    // Submits the form to the server. delay for ball drop animation. reassigns draggable ball back to its ball bag container
        setTimeout(() => {
            console.log('after timeout ' + targetValue);
            liveSend(String(targetValue)) // sends player choice to server
            draggable.style.removeProperty("position"); 
            draggable.style.removeProperty("top"); 
            ballContainer.append(draggable); 
        }, 80);
    }

/* ========== BALL DROP ANIMATION ========== */
    /* functions for ball drop event -- happens on the ball */ // from https://www.w3schools.com/howto/howto_js_animate.asp
    function ballDrop(draggable) {
        var elem = draggable;//document.getElementById("draggable_ball");
        var pos = 0;
        clearInterval(animateInterval);
        animateInterval = setInterval(frame, 15); // the lower the number, the faster it falls
        function frame() {
            if (pos == 65) { // can make it fall farther into the bucket by increasing this
                clearInterval(animateInterval);
            } else {
                pos++;
                elem.style.top = pos + 'px';
            }
        }
    }


/* ========== LIVE RECEIVE ========== */
    function liveRecv(data) {
        console.log('data.puedeSeguir says ' + data.puedeSeguir);
        bucketPayoffs_01 = data.bucket_01_payoffs;
        bucketPayoffs_02 = data.bucket_02_payoffs; 
        nBallsLeft = data.balls_remaining;
        totalPayoff = data.total_earnings;
        set_display(bucketPayoffs_01, bucketPayoffs_02, nBallsLeft, totalPayoff);
        nBallsinBucket01 = data.balls_in_bucket01;
        nBallsinBucket02 = data.balls_in_bucket02;
        fillThemBuckets(nBallsinBucket01, nBallsinBucket02);
        if (data.puedeSeguir === false) {
            document.getElementById("form").submit(); // document.location.reload();
        }
    }


/*  ========== Buckets Filling Up with Balls Script ========== */
    // 1) fill each bucket with the number of balls already allocated to each bucket
        // 1.a) requires the total number of balls already allocated to each bucket
            // i.e., "js_vars.bucket_01_num_balls" and "js_vars.bucket_02_num_balls"
    // 2) ensures that the balls populating the buckets do not interfere with the drag-and-drop event
        // by applying the class "binis01" or "binis02" to each ball as appropriate

    var nBallsinBucket01, nBallsinBucket02;

    function fillThemBuckets(nBallsinBucket01, nBallsinBucket02) {
        let Bucket02 = document.getElementById('Bucket02'); // finds the flex-container Bucket_02 and creates a javascript variable for it; seems to conflict with rest of script if declared outside of the function as a constant
        let Bucket01 = document.getElementById('Bucket01'); // finds the flex-container Bucket_01 and creates a javascript variable for it; seems to conflict with rest of script if declared outside of the function as a constant
        while (Bucket02.firstChild) {
            Bucket02.removeChild(Bucket02.firstChild);
        }
        for (var i=1; i<=nBallsinBucket02; i++) { // creates a div element for each ball previously allocated to Bucket_02
            let ball_02 = document.createElement("div"); // each ball is its own div element
            ball_02.setAttribute("class", "binnedBall"); // applies the class "binnedBall" to the div so that it behaves according to the stylesheet
            ball_02.classList.add('binis02'); // applies the class "binis02" to the div so that balls dragged on top of the pre-existing balls within the bucket do not interfere with the drop event
            Bucket02.append(ball_02); // makes the ball a flex-item child of the flex-container Bucket_02
        }
        while (Bucket01.firstChild) {
            Bucket01.removeChild(Bucket01.firstChild);
        }
        for (var i=1; i<=nBallsinBucket01; i++) { // creates a div element for each ball previously allocated to Bucket_01
            let ball_01 = document.createElement("div"); // each ball is its own div element
            ball_01.setAttribute("class", "binnedBall"); // applies the class "binnedBall" to the div so that it behaves according to the stylesheet
            ball_01.classList.add('binis01'); // applies the class "binis01" to the div so that balls dragged on top of the pre-existing balls within the bucket do not interfere with the drop event
            Bucket01.append(ball_01); // makes the ball a flex-item child of the flex-container Bucket_01 
        }
    }


/* ========== DOM CONTENT LOADED EVENT ========== */
    document.addEventListener('DOMContentLoaded', function (event) {
        bucketPayoffs_01 = js_vars.bucket_01_payoffs;
        bucketPayoffs_02 = js_vars.bucket_02_payoffs; 
        nBallsLeft = js_vars.balls_remaining;
        totalPayoff = js_vars.total_earnings;
        set_display(bucketPayoffs_01, bucketPayoffs_02, nBallsLeft, totalPayoff);
        nBallsinBucket01 = js_vars.balls_in_bucket01;
        nBallsinBucket02 = js_vars.balls_in_bucket02;
        fillThemBuckets(nBallsinBucket01, nBallsinBucket02);
    });




