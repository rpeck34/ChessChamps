/* For my own original events, need to create them here first.
Then they can be listend to using add event listener, onclick etc. 
*/

const connectEvent = new CustomEvent('connectedSuccess');
document.addEventListener('connectedSuccess', connectedSuccess);
const startEvent = new CustomEvent("championCreated");
document.addEventListener("championCreated", championCreated);

function connectedSuccess(){
	console.log('USER CONNECTED');
}

function championCreated(){
	console.log("the event fired")
	//redirect to new url only if we can create a new champion
	location.href='champion_manager'
}

//battle screen onClick functions
function playFriend(element, color) {
  element.style.color = color;
}

function playRandom(element, color, userid, elo, 
[low, high], blocked) {
	element.style.color = color;
	socket.emit('play_message', "finding match...");
	socket.emit('play_random', userid, elo, 
	[low, high], blocked)
}

//champions screen onClick functions
function selectChampion(element, champClass) {
	//change selected champ for user in db
	console.log("selecting champ")
	socket.emit('selectChampion', champClass)
	//redirect to that champions champion_manager page
	location.href='champion_manager'
}

function deleteChampion(element) {
	console.log('deleting champion')
	socket.emit('deleteChampion')
	location.href='champions'
}
	
function createChampion(element, champClass) {
	console.log('creating champion')
	socket.emit('createChampion', champClass)
}

//champ_manager onClick functions
function submitTalents(element) {
	//send talents into here as json?
	socket.emit('submitTalents')
}

function undoTalents(element) {
	//python event will reload talents from db to html page here
	socket.emit('undoTalents')
}

function readyForBattle(element) {
	//simple relocation to battle page
	location.href='battle'
}