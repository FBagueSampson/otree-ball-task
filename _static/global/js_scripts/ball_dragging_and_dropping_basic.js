/*  ==== Ball Dragging and Dropping Script ==== */

/* draggable element: ball */
    const item = document.querySelector('.ball'); // finds html elements of class="ball"

/* event listeners for the ball */
    item.addEventListener('dragstart', dragStart); // listens for start of dragging ball
    item.addEventListener('dragend', dragStop); // listens for end of dragging ball, wherever that happens

/* functions for ball events */
    function dragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.id); // grabs the id of the ball, "draggable_ball"
        event.target.classList.add('while-dragging'); // adds the class "while-dragging" to the element on the event
    }

    function dragStop(e) {
        event.target.classList.remove('while-dragging'); // removes the class "while-dragging" to the element on the event
    }

/* drop targets: buckets */
    const buckets = document.querySelectorAll('.droppable'); // finds html elements of class="droppable"

/* event listeners for the buckets */
    /* applies each event listener to all buckets on page */
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

/* functions for drop event -- happens on the buckets */
    function dropOn(e) {
        event.preventDefault();
        e.target.classList.remove('drag-over'); // removes the class "drag-over" to the element on the event

    // capture choice of bucket and send to server (alllows choice of bucket to be robust to placing ball on the binned balls)
        if (e.target.id == "Bucket02" || e.target.classList.contains("binis02") ) {
            targetValue = 'bucket_02';
            chosenBucket = document.getElementById('Bucket02');
        } else if (e.target.id == "Bucket01" || e.target.classList.contains("binis01") ) {
            targetValue = 'bucket_01';
            chosenBucket = document.getElementById('Bucket01');
        }
        
        forminputs.bucket.value = targetValue; // set the value of the form before submitting
        
    // get the draggable element
        const id = e.dataTransfer.getData('text/plain'); // returns the id of the ball, "draggable_ball"
        const draggable = document.getElementById(id); // grabs the <div> element with id="id"

    // attach the ball to the drop target
        chosenBucket.appendChild(draggable);

    // return display color of the ball to the original pre-dragged style
        draggable.classList.remove('while-dragging');

    // for ball-drop event below. want it delayed? change that 0 to something else
        setTimeout(() => {
            draggable.style.position = 'absolute'; // required for javascript ball-falling
            ballDrop(draggable);
        }, 0);

        // NEW moved here from below; submits the form to the server. delay for ball drop animation
        setTimeout(() => {
            document.getElementById("form").submit();
          }, 80);
    }

/* functions for ball drop event -- happens on the ball */
    // from https://www.w3schools.com/howto/howto_js_animate.asp
        //var animateInterval = null;
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
                //elem.style.left = pos + 'px';
            }
        }
    }


