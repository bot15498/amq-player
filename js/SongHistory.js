// ==UserScript==
// @name         AMQ Song History
// @version      1.0.0
// @description  Adds song tracking and submitting to external site.
// @author       you
// @connect      localhost
// @match        https://animemusicquiz.com/*
// @grant        GM_xmlhttpRequest
// ==/UserScript==

// don't load on login page
if (document.getElementById("startPage")) return;

// Wait until the LOADING... screen is hidden and keep trying to load script until it laods. 
let loadInterval = setInterval(() => {
    if (document.getElementById("loadingScreen").classList.contains("hidden")) {
        setup();
        clearInterval(loadInterval);
    }
}, 500);

let onResultListener;
let onNextSongListener;
let songHistoryUrl = 'http://localhost:3001/';

function setup() {
    onResultListener = new Listener('answer results', onAnswerResult);
    onNextSongListener = new Listener('play next song', onNextSong);

    onResultListener.bindListener();
    onNextSongListener.bindListener();
}

function onAnswerResult(result) {
    // collect data to send to webapp
    const you = getSelf()
    if(you.length !== 0 && 'catbox' in result.songInfo.urlMap) {
        // get the highest res video
        var catboxUrl = "huh";
        if ('720' in result.songInfo.urlMap.catbox) {
            catboxUrl = result.songInfo.urlMap.catbox['720'];
        } else if ('480' in result.songInfo.urlMap.catbox) {
            catboxUrl = result.songInfo.urlMap.catbox['480'];
        } else {
            catboxUrl = result.songInfo.urlMap.catbox['0'];
        }

        var payload = {};
        // console.log(result);
        payload.songInfo = {animeNameEN: result.songInfo.animeNames.english, 
                            animeNameJP: result.songInfo.animeNames.romaji, 
                            siteIds: result.songInfo.siteIds, 
                            songName: result.songInfo.songName,
                            artist: result.songInfo.artist,
                            // very ugly I cry
                            id: catboxUrl.split('catbox.moe/').slice(-1)[0].split('.')[0],
                            difficulty: result.songInfo.animeDifficulty
                        };
        payload.playerInfo = {answer: you[0].avatarSlot.$answerContainerText.text(),
                                correct: result.players[you[0].gamePlayerId].correct,
                                username: you[0]._name
                        };

        // make post request
        const jsonString = JSON.stringify(payload);
        GM_xmlhttpRequest({
            method: 'POST',
            url: songHistoryUrl + 'submit/' + payload.songInfo.id,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            data: 'data=' + encodeURIComponent(jsonString),
            onload: (resp) => {
                // update stats info.
                const responsePayload = JSON.parse(resp.responseText);
                console.log(resp);
                console.log(responsePayload);
                addStatsToSongInfo(responsePayload)
            },
            onerror: (resp) => {
                console.log('Got back error when posting data.');
                console.log(resp);
                gameChat.systemMessage('Failed to post / get song history info. Is the server running?');
            }
        })
    }
}

function onNextSong(result) {
    // clear out stats since they don't disappear. 
    clearSongInfoStats();
}

function addStatsToSongInfo(payload) {
    // sets the stats on the song info modal. 
    // clear if something is there.
    clearSongInfoStats();
    // get base object (the bottom links)
    const linkRowDiv = $('#qpSongInfoLinkRow');

    if(linkRowDiv.length !== 0) {
        if('numPlays' in payload) {
            const numPlays = payload.numPlays;
            linkRowDiv.before(`<div id="numPlaysDiv" class="row">Played <b>${numPlays}</b> times!</div>`);
        }
        if('numCorrect' in payload) {
            const numPlays = payload.numPlays;
            const numCorrect = payload.numCorrect;
            const correctRate = numCorrect/numPlays * 100;
            linkRowDiv.before(`<div id="numCorrectDiv" class="row"><b>Answer rate:</b> ${numCorrect}/${numPlays} (${correctRate.toFixed(2)} %)</div>`);
        }
        if('lastPlayed' in payload) {
            const lastPlayed = payload.lastPlayed;
            linkRowDiv.before(`<div id="lastPlayedDiv" class="row"><b>Last played:</b> ${lastPlayed}</div>`);
        }
        if('historyLink' in payload) {
            const historyLink = payload.historyLink;
            linkRowDiv.before(`<div id="historyLinkDiv" class="row"><a href="${historyLink}" target="_blank">Show More</a></div>`);
        }
    }
}

function clearSongInfoStats() {
    const numPlaysDiv = $('#numPlaysDiv');
    const numCorrectDiv = $('#numCorrectDiv');
    const lastPlayedDiv = $('#lastPlayedDiv');
    const historyLinkDiv = $('#historyLinkDiv');
    if(numPlaysDiv.length !== 0) {
        numPlaysDiv.remove();
    }
    if(numCorrectDiv.length !== 0) {
        numCorrectDiv.remove();
    }
    if(lastPlayedDiv.length !== 0) {
        lastPlayedDiv.remove();
    }
    if(historyLinkDiv.length !== 0) {
        historyLinkDiv.remove();
    }
}

function getSelf() {
    // we only care about ourself (for now)
    return Object.values(quiz.players).filter(player => player.isSelf);
}