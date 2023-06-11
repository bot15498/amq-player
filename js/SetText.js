// ==UserScript==
// @name         AMQ End Screen Text Changer.
// @version      1.0.0
// @description  Change the text on the final score screen.
// @author       you
// @match        https://animemusicquiz.com/*
// @grant        none
// ==/UserScript==

// don't load on login page
if (document.getElementById("startPage")) return;

// Wait until the LOADING... screen is hidden and load script
let loadInterval = setInterval(() => {
    if (document.getElementById("loadingScreen").classList.contains("hidden")) {
        setup();
        clearInterval(loadInterval);
    }
}, 500);

let command = "/set"
let command2 = "ggs["

function setTextById(strToCopy, id) {
    $(id).text(strToCopy)
}

function setTextSongContainer(strToCopy) {
    let songContainer = $("#qpSongInfoContainer");
    // Change "song info" text
    let songInfoTxt = songContainer.children().first().children().first().text()
    songInfoTxt = songInfoTxt.replace("Song Info", strToCopy + " info");
    songContainer.children().first().children().first().text(songInfoTxt);

    // Change Song name
    let songNameTxt = songContainer.children().eq(1).children().first().children().first().text();
    songNameTxt = songNameTxt.replace("Song Name", strToCopy + " name");
    songContainer.children().eq(1).children().first().children().first().text(songNameTxt);
    setTextById(strToCopy, "#qpSongName");

    // Change artist text
    let songArtistText = songContainer.children().eq(2).children().first().children().first().text();
    songArtistText = songArtistText.replace("Artist", strToCopy + "ist");
    songContainer.children().eq(2).children().first().children().first().text(songArtistText);
    setTextById(strToCopy, "#qpSongArtist");

    // Change song type
    setTextById(strToCopy + " Song", "#qpSongType");

    // Change song links
    setTextById(strToCopy + " video", "#qpSongVideoLink");
    setTextById(strToCopy + " anime", "#qpAnimeLink");

    // Change report button
    let reportText = $("#qpReportContainer").children().eq(0).text();
    reportText = reportText.replace("Report", strToCopy);
    $("#qpReportContainer").children()[0].innerText = reportText;
}

function setTextStandings(strToCopy) {
    let standingContainer = $("#qpStandingContainer");

    // Change player names
    $(".qpsPlayerName").text(strToCopy);
    
    // Change "standings"
    let standingsText = standingContainer.children().eq(0).children().eq(0).text();
    standingsText = standingsText.replace("Standings", strToCopy + "ings");
    standingContainer.children().eq(0).children().eq(0).text(standingsText)
}

function setup() {
    console.log("loaded set");
    let commandListener = new Listener("game chat update", (data) => {
        data.messages.forEach(message => {
            if (message.sender === selfName && (message.message.startsWith(command) || message.message.startsWith(command2))) {
                let commandArgs = message.message.split(/\s+/);
                // create string
                if(commandArgs.length == 1) {
                    commandArgs[1] = "sex";
                }

                if (commandArgs[1] !== undefined) {
                    // recreate the string to copy everywhere.
                    let strToCopy = commandArgs.filter((val, i) => i != 0).join(" ");

                    // Change the answer name
                    setTextById(strToCopy, "#qpAnimeName");

                    // Change song count at the top
                    setTextById(strToCopy, "#qpCurrentSongCount");
                    setTextById(strToCopy, "#qpTotalSongCount");

                    // Change song info container
                    setTextSongContainer(strToCopy);

                    // Change player answers
                    $("#qpAnswerInput").val(strToCopy);
                    $(".qpAvatarAnswerText").text(strToCopy);
                    $(".qpAvatarName").text(strToCopy);
                    $(".qpAvatarLevel").text(strToCopy);

                    // Change name in standings
                    setTextStandings(strToCopy)

                    // Change leave button
                    $("#qpLeaveButton").children()[0].innerText = strToCopy + " ?"
                }
            }
        });
    });

    commandListener.bindListener();
}
