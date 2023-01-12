let mesAtual = String((new Date().getUTCMonth()));
let  diaJs;
let diaExibido = document.getElementsByClassName('data-visualizada');
let caixaDia = document.getElementsByClassName('dias');

for (let i=0; i < diaExibido.length; i++){ 
    diaJs = String(new Date(diaExibido[i].innerText).getUTCMonth());  
      
    if (diaJs != mesAtual){
        console.log(diaJs +  "!=" + mesAtual);
        diaExibido[i].style.color = 'lightgray';
        caixaDia[i].style.backgroundColor = 'lightslategray';
    }
   diaExibido[i].innerText = new Date(diaExibido[i].innerText).getUTCDate()
}
 
function abrir(){
    document.getElementById("menuItens").classList.toggle("show");
}

window.onclick = function(event){
    if(!event.target.matches('.droparbtn')){
        let dropdowns = document.getElementsByClassName("conteudoDrop");
    }
    let i;
    for(i=0; i < dropdowns.length; i++){
        let openDropdown = dropdowns[0];
        if(openDropdown.classList.contains('show')){
            openDropdown.classList.remove('show');
        }
    }
}




