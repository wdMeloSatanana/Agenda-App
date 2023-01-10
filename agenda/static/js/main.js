let mesAtual = String((new Date().getUTCMonth()));
const dia = document.getElementsByClassName("dias");
let  diaJs;

for (let i=0; i < dia.length; i++){ 
    diaJs = String(new Date(dia[i].innerText).getUTCMonth());
    if (diaJs != mesAtual){
        console.log(diaJs +  "!=" + mesAtual);
        dia[i].style.color = 'white';
    }
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