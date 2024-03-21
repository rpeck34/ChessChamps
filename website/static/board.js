const board = document.querySelector("#board")
const width = 8
const length = 8
let turn = 'white'
const startPieces = [
	wR, wN, wB, wQ, wK, wB, wN, wR,
	wP, wP, wP, wP, wP, wP, wP, wP,
	'', '', '', '', '', '' ,'' ,'',
	'', '', '', '', '', '' ,'' ,'',
	'', '', '', '', '', '' ,'' ,'',
	'', '', '', '', '', '' ,'' ,'',
	bP, bP, bP, bP, bP, bP, bP, bP,
	bR, bN, bB, bQ, bK, bB, bN, bR,
	]
	
function createBoard() {
	startPieces.forEach((startPiece, i) => {
		const square = document.createElement('div')
		square.classList.add('square')
		square.innerHTML = startPiece
		square.setAttribute('square-id', i)
		const row = Math.floor((63 - i) / 8)
		const col = (i + 1) % 8
		square.classList.add((row + col) % 2 ? "brown" : "beige")
		board.append(square)
	})
}
createBoard()

//should grab all squares from board in html
const allSquares = document.querySelectorAll('#board .square')

//go through all squares and wait for dragStart event
allSquares.forEach(square => {
	//all these drag events are premade default things we can
	//listen for built into javascript language
	square.addEventListener('dragstart', dragStart)
	square.addEventListener('dragover', dragOver)
	square.addEventListener('drop', dragDrop)
})

//let x initiates variable x as null
let startPositionId
let draggedElement

//drag pieces
function dragStart (e) {
	startPositionID = e.target.parentNode.getAttribute('square-id')
	draggedElement = e.target
}

function dragOver(e) {
	e.preventDefault()
}

function dragDrop (e) {
	//stops weird unwanted default behvaiour of dragdrop
	e.stopPropagation()
	const taken = e.target.classList.contains('piece')
	e.target.parentNode.append(draggedElement)
	e.target.remove()
}