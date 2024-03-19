/*  ==== Buckets Filling Up with Balls Script ==== */
    // 1) fill each bucket with the number of balls already allocated to each bucket
        // 1.a) requires the total number of balls already allocated to each bucket
        // i.e., "js_vars.bucket_01_num_balls" and "js_vars.bucket_02_num_balls"
    // 2) ensures that the balls populating the buckets do not interfere with the drag-and-drop event
        // by applying the class "binis01" or "binis02" to each ball as appropriate
    
        var Bucket02 = document.getElementById('Bucket02'); // finds the flex-container Bucket_02 and creates a javascript variable for it
        var Bucket01 = document.getElementById('Bucket01'); // finds the flex-container Bucket_01 and creates a javascript variable for it
        
        for (var i=1; i<=js_vars.bucket_02_num_balls; i++) { // creates a div element for each ball previously allocated to Bucket_02
            let ball_02 = document.createElement("div"); // each ball is its own div element
            ball_02.setAttribute("class", "binnedBall"); // applies the class "binnedBall" to the div so that it behaves according to the stylesheet
            ball_02.classList.add('binis02'); // applies the class "binis02" to the div so that balls dragged on top of the pre-existing balls within the bucket do not interfere with the drop event
            Bucket02.append(ball_02); // makes the ball a flex-item child of the flex-container Bucket_02
        }
        
        for (var i=1; i<=js_vars.bucket_01_num_balls; i++) { // creates a div element for each ball previously allocated to Bucket_01
            let ball_01 = document.createElement("div"); // each ball is its own div element
            ball_01.setAttribute("class", "binnedBall"); // applies the class "binnedBall" to the div so that it behaves according to the stylesheet
            ball_01.classList.add('binis01'); // applies the class "binis01" to the div so that balls dragged on top of the pre-existing balls within the bucket do not interfere with the drop event
            Bucket01.append(ball_01); // makes the ball a flex-item child of the flex-container Bucket_01 
        }