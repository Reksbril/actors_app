function changeMyCharacterName(characterName) {
    var currentCharacterName = document.getElementById("my_character_name");
    currentCharacterName.setAttribute("data-character-name", characterName);
}

function closeCharacterSelectionPopup() {
    var popupDiv = document.getElementById("popup_div_id");
    popupDiv.style.display = "none";
}

function dialogueElementOnClick(dialogueElementId) {
    var audioPlayerWrapper = document.getElementById("audio_player_wrapper_id_" + dialogueElementId);
    var audioSourceUrl = audioPlayerWrapper.getAttribute("data-audio-url");

    var myCharacterName = document.getElementById("my_character_name").getAttribute("data-character-name");
    var currentCharacterName = audioPlayerWrapper.getAttribute("data-character-name");

    if (myCharacterName.toLowerCase() == currentCharacterName.toLowerCase()) {

        var audioElement = document.getElementById("global_audio_player");
        audioElement.pause();
        audioElement.removeAttribute("controls");

        var nextButton = document.getElementById("next_button");
        nextButton.style.display = "flex";
        nextButton.onclick = () => {
            nextButton.style.display = "none";
            dialogueElementOnClick(dialogueElementId + 1);
        }
        audioPlayerWrapper.appendChild(nextButton);
    } else {
        var audioElement = document.getElementById("global_audio_player");
        audioPlayerWrapper.appendChild(audioElement);
        audioElement.setAttribute("controls", "");
        audioElement.src = audioSourceUrl;
        audioElement.play();
        audioElement.onended = () => {
            audioElement.removeAttribute("controls");
            dialogueElementOnClick(dialogueElementId + 1);
        };
    }







}