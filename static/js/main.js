function fireConfetti() {
    confetti({
        particleCount: 200,
        spread: 100,
        origin: { y: 0.4 }
    });
}


function logout() {
    $.ajax({
        type: 'POST',
        url: '/logout',
        success: function(response) {
            location.href = '/login';
            alert(response.msg);
        },
    });
}


function getTodayDateString() {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
}

function markTodayAttendance() {
    const todayStr = getTodayDateString();
    const cell = document.querySelector(`#grassGrid div[data-date="${todayStr}"]`);
    if (cell) {
        cell.classList.remove("level-0");
        cell.classList.add("level-1");
    }
}


//유저가 도전권을 사용하여 도전한 경우 작동하는 함수
function guessMoney(){
    let money = $("#user-input-money").val()
    $.ajax({
        type:"POST",
        url:"/apply",
        data:{appPrice:money},

        error: function (xhr) {
           // xhr.responseJSON
        },

        success:function(response){
            if(response["result"]=="success"){
                popupSuccess();
                fireConfetti();
                updateTicketCount(); 
                updateRecordList();

                if (response["isFirstAttendance"]) {
                    markTodayAttendance(); 
                    updateCalendar();
                }
            }
            else{
                popupfail();
            }
        }
    })

}

function updateRecordList() {
    $.ajax({
        type: 'GET',
        url: '/getApplist',
        success: function (response) {
            if (response.result === 'success') {
                const list = response.appList;
                const container = $("#past_record ul");
                container.empty(); 
                
                list.forEach(user => {
                    const date = user.appDate.slice(0, 10);
                    const time = user.appDate.slice(11, 16);
                    const price = user.appPrice;
                    const html = `
                        <li class="flex justify-between items-center bg-gray-100 px-4 py-3 rounded-lg shadow hover:shadow-md transition">
                            <span class="text-emerald-600 font-medium">${price}원</span>
                            <span class="text-sm text-gray-500">${date} ${time}</span>
                        </li>`;
                    container.append(html);
                });
            }
        }
    });
}


function updateTicketCount() {
    $.ajax({
        type: 'GET',
        url:'/getTicketCount',
        success: function (response) {
            document.getElementById("ticket-count").innerText = `보유 도전권: ${response.appTicket}개`;
        }
    });
}



function addCouponAlert(){
    const ticketBtn = document.getElementById('everyCouponAlert')
    ticketBtn.classList.remove('opacity-0', 'pointer-events-none'); // 보이게
    ticketBtn.classList.add('opacity-100'); 

    setTimeout(() => {
        ticketBtn.classList.remove('opacity-100'); 
        ticketBtn.classList.add('opacity-0', 'pointer-events-none'); 
    }, 2000);
}

function addEveryDayTicket(){
    $.ajax({
        type:"POST",
        url:"/ticket/free",
        success:function(response){
            if(response["result"]=="success"){
                updateTicketCount();
            }
            else{
                addCouponAlert();
            }
        }
    })
}

function addCommitTicket(){
    $.ajax({
        type:"POST",
        url:"/ticket",
        success:function(response){
            if(response["result"]=="success"){
                updateTicketCount();
            }
            else{
                addCouponAlert();
            }
        }
    })
}

function popupSuccess(){
    const successDiv = document.getElementById('popup-user-record');
    if (successDiv.classList.contains('hidden')) {
        successDiv.classList.remove('hidden');
    } 
    else {
    successDiv.classList.add('hidden');
}}

function popupfail(){
    const failDiv = document.getElementById('popup-user-fail');
    if (failDiv.classList.contains('hidden')) {
        failDiv.classList.remove('hidden');
    } 
    else {
    failDiv.classList.add('hidden');
}}

function popupTicket(){
    const ticketDiv = document.getElementById('popup-ticket');
    if (ticketDiv.classList.contains('hidden')) {
        ticketDiv.classList.remove('hidden');
    } 
    else {
    ticketDiv.classList.add('hidden');
}}

function toggle_record(){
    const recordDiv = document.getElementById('past_record');
    if (recordDiv.classList.contains('hidden')) {
        recordDiv.classList.remove('hidden');
    } 
    else {
    recordDiv.classList.add('hidden');
}}