window.onload = function init(){
    $(".main").css("display", "none")
    $("#login").css("display", "")
    //$("#Familiar").css("display", "")
}

var CountTime = new Object;

function loginEvent(){
    userID = $("#inputID").val();;
    pw = $("#inputPassword").val();
    console.log(userID, pw);

    url = "/api/login?userId="+userID+"&pw="+pw;
    console.log(url)
    data = fetch(url)
        .then(function(response) {
            data = response.json().then(function(data){
                if(data.status == "login successful"){
                    console.log(data.status)
                    $("#login").css("display", "none")
                    $("#introTheExperiment").css("display", "")
                    Cookies.set("status", "introTheExperiment", { expires: 7 });
                    Cookies.set("userID", userID, { expires: 7 });
                    Cookies.set("userPW", pw, { expires: 7 });
                }
                else{
                    $("#inputID").val("");
                    $("#inputPassword").val("");
                    alert("登入失敗，請檢查帳號密碼後再試一次")
                }
            })
        })

    //request and successful

}

function introAgreed(){
    showImg()
}

function sleep(second) {
    return new Promise(resolve => setTimeout(resolve, second * 1000));
  }

function showImg(){
    //get img
    //put it into targetImg
    url = "/api/getNextImg";
    console.log(url)
    data = fetch(url)
        .then(function(response) {
            data = response.json().then(function(data){
                console.log(data);
                if(data.status == "get successful"){
                    console.log(data.status)
                    Cookies.set("status", "showImg", { expires: 7 });
                    Cookies.set("imgId", data.imgId, { expires: 7 });
                    document.getElementById('targetImg')
                    .setAttribute(
                        'src', 'data:image/png;base64,'+data.pic_b64
                    );
                    $(".main").css("display", "none")
                    $("#showImg").css("display", "")
                    
                    CountTime.t0_watchImg = performance.now() //開始計時
                    setTimeout(function () {
                        console.log(data.timeout, "秒到了 ", (performance.now() - CountTime.t0_seeImg)/1000)
                        if(Cookies.get("status")=="showImg"){
                        startAnswering()
                        }
                    }, data.timeout*1000);
                }else if (data.status == "no more image"){
                    alert("你的帳號已經結束實驗")
                }else if (data.status == "user verify error"){
                    alert("你的帳號出現問題，請重新登入")
                    $(".main").css("display", "none")
                    $("#login").css("display", "")
                }
            })
        })
}

var haveAnswer = false;
function startAnswering(){
    //stop counting time
    costTime = (performance.now() - CountTime.t0_watchImg)/1000
    Cookies.set("status", "Answering", { expires: 7 });
    Cookies.set("timeCostInWatch", costTime, { expires: 7 });
    CountTime.t0_nameImg = performance.now() //開始計時
    setTimeout(function () {document.getElementById("answer").focus();}, 100);
    document.getElementById('answer').value = ""
    $(".main").css("display", "none")
    $("#Answering").css("display", "")
    haveAnswer = false;
    // 本頁面，暫定無限制時間
}

function submitAnsToFamiliar(){
    if(haveAnswer == false){
        alert("請先輸入答案再進入下一步")
        return 0;
    }else{
        costTime = (performance.now() - CountTime.t0_nameImg)/1000
        Cookies.set("status", "Familiar", { expires: 7 });
        Cookies.set("timeCostInName", costTime, { expires: 7 });
        CountTime.t0_familiarImg = performance.now() //開始計時
        setTimeout(function () {document.getElementById("answer").focus();}, 100);
        Cookies.set("imgName", document.getElementById('answer').value, { expires: 7 })
        $(".main").css("display", "none")
        $("#Familiar").css("display", "")
        // document.getElementById('answerBar').value = 0
        haveAnswer = false;
        
        var radionum = document.getElementsByName("familiarRad");
        for (var i = 0 ; i < radionum.length ; i++ ) {
            radionum[i].checked = false ;
        } 
    }
}

function updateBar(){
    haveAnswer = true;
    document.getElementById('familiarTitle').innerHTML = "熟悉程度："+String(document.getElementById('answerBar').value)
}

function submitAnsToServer(){
    //取 radio 的 value
    var radionum = document.getElementsByName("familiarRad");
    var result = 0 ;
    for (var i = 0 ; i < radionum.length ; i++ ) {
        if (radionum[i].checked) {
            result = radionum[i].value
            haveAnswer = true ;
        }
    }

    if(haveAnswer == false){
        alert("請先選擇熟悉程度再進入下一步")
        return 0;
    }
    costTime = (performance.now() - CountTime.t0_familiarImg)/1000
    Cookies.set("timeCostInFamiliar", costTime, { expires: 7 });

    Cookies.set("imgFamiliar", result, { expires: 7 })   

    outData = Object()
    outData.userID = Cookies.get("userID")
    outData.imgName = Cookies.get("imgName")
    outData.imgId = Cookies.get("imgId")
    outData.imgFamiliar = Cookies.get("imgFamiliar")
    outData.timeCostInWatch = Cookies.get("timeCostInWatch")
    outData.timeCostInName = Cookies.get("timeCostInName")
    outData.timeCostInFamiliar = Cookies.get("timeCostInFamiliar")
    console.log(JSON.stringify(outData))


    url = "/api/sendRecord"+"?data="+JSON.stringify(outData);
    console.log(url)
    data = fetch(url)
        .then(function(response) {
            data = response.json().then(function(data){
                if(data.status == "send success"){
                    restForWhile(parseInt(data.restTime))
                }else if (data.status == "user verify error"){
                    alert("你的帳號出現問題，請重新登入")
                    $(".main").css("display", "none")
                    $("#login").css("display", "")
                }
            })
        })

}

var restTimer = null;
var restIndex = 0;
var restStart = performance.now()
var restTimeForCheck = 0;

function restForWhile(restTime){
    console.log("休息時間")
    Cookies.set("status", "restForWhile", { expires: 7 });
    startTime = performance.now()
    originText = document.getElementById("restForWhileButton").innerHTML
    $(".main").css("display", "none")
    $("#restForWhile").css("display", "")
    document.getElementById('familiarTitle').innerHTML = "熟悉程度"
    
    document.getElementById("restForWhileButton").innerHTML = originText + "(" + String(restTime) + ")"
    restIndex = restTime
    restStart = performance.now()
    restTimeForCheck = restTime;
    restTimer = setInterval(modifyRestTime, 1000);
}

function modifyRestTime(){
    restIndex -= 1
    document.getElementById("restForWhileButton").innerHTML = "開始下一題(" + String(restIndex) + ")"
    if((performance.now() - restStart)/1000  > restTimeForCheck){
        clearInterval(restTimer);
        document.getElementById("restForWhileButton").innerHTML = "開始下一題"
        showImg()
    }
}