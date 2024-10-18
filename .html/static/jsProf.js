function editActive(){
	var editButton = document.getElementById("edit");
	var save = document.getElementById("save");
	var nome = document.getElementById("nome");
	var email = document.getElementById("email");
	var end = document.getElementById("end");
	var tel = document.getElementById("tel");
	var cpf = document.getElementById("cpf");
	var del = document.getElementById("delete");
	
	editButton.style.display = "none";
	save.style.display = "inline-block";
	del.style.display = "inline-block";
	
	nome.classList.remove("fakeInputDisabled");
	email.classList.remove("fakeInputDisabled");
	end.classList.remove("fakeInputDisabled");
	tel.classList.remove("fakeInputDisabled");
	cpf.classList.remove("fakeInputDisabled");
	
	if(end.value == "Não Definido"){
		end.value = ""
	};
	if(tel.value == "Não Definido"){
		tel.value = ""
	};
	if(cpf.value == "Não Definido"){
		cpf.value = ""
	};
	
	nome.disabled = false;
	email.disabled = false;
	end.disabled = false;
	tel.disabled = false;
	cpf.disabled = false;
};

function correctEmpty(){
	var end = document.getElementById("end");
	var tel = document.getElementById("tel");
	var cpf = document.getElementById("cpf");
	
	if(end.value == ""){
		end.value = "Não Definido"
	};
	if(tel.value == ""){
		tel.value = "Não Definido"
	};
	if(cpf.value == ""){
		cpf.value = "Não Definido"
	};
};

function resetAll(){
	var editButton = document.getElementById("edit");
	var save = document.getElementById("save");
	var nome = document.getElementById("nome");
	var email = document.getElementById("email");
	var end = document.getElementById("end");
	var tel = document.getElementById("tel");
	var cpf = document.getElementById("cpf");
	var del = document.getElementById("delete");
	
	editButton.style.display = "inline-block";
	save.style.display = "none";
	del.style.display = "none";
	
	nome.classList.add("fakeInputDisabled");
	email.classList.add("fakeInputDisabled");
	end.classList.add("fakeInputDisabled");
	tel.classList.add("fakeInputDisabled");
	cpf.classList.add("fakeInputDisabled");
	
	nome.disabled = true;
	email.disabled = true;
	end.disabled = true;
	tel.disabled = true;
	cpf.disabled = true;
}

function popUp(){
	var popup = document.getElementById("popUpB");
	var popupW = document.getElementById("popUpWindow");
	
	popup.style.display = "flex";
	popupW.style.top = "15%";
};

function popDown(){
	var popup = document.getElementById("popUpB");
	var popupW = document.getElementById("popUpWindow");
	
	popup.style.display = "none";
	popupW.style.top = "150%";
};

function validateForm(){
	resetAll();
	
	const url = new URLSearchParams(window.location.search);
	const val = url.get('error');
	

	if (val === '1') {
		editActive();
		var n = document.getElementById("email");
		
		n.style.border = ("solid 2px red");
	};
	if (val === '2') {
		editActive();
		popUp();
		var n = document.getElementById("nomeD");
		var e = document.getElementById("emailD");
		var p = document.getElementById("passD");
		
		n.style.border = ("solid 2px red");
		e.style.border = ("solid 2px red");
		p.style.border = ("solid 2px red");
	}
};

function validadeCredentials(){
	var accessValue = document.getElementById("accessValue").textContent;
	
	// Admin 3
	// Funcionario 2
	// Carente 1
	// Nada 0
	if (accessValue == 3){
		var volunButton = document.getElementById("volunButton")
		volunButton.style.display = "block";
	};
	if (accessValue >= 2){
		var estoqButton = document.getElementById("estoqButton")
		estoqButton.style.display = "block";
	};
}

function onLoadHandler(){
	validadeCredentials();
	validateForm();
}