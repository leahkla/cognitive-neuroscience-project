let sliders, sliderfills, thumbs, slidervalues;
let initialValue; //initial values for the sliders

document.addEventListener('DOMContentLoaded', function (e) { init();});

function init(){
  sliders = document.querySelectorAll(".customrange");
  sliderfills = document.querySelectorAll(".sliderfill");
  thumbs = document.querySelectorAll(".sliderthumb");
  slidervalues = document.querySelectorAll(".slidervalue");
  /* We need to change slider appearance to respond to both input and change events. */
  for (let i=0;i<sliders.length;i++){
    sliders[i].addEventListener("input",function(e){updateSlider(i,sliders[i].value);});
    sliders[i].addEventListener("change",function(e){updateSlider(i,sliders[i].value);});
    //set initial values for the sliders
    sliders[i].value = Number(sliders[i].getAttribute("value"));
    //update each slider
    updateSlider(i,sliders[i].value);
  }
}
function updateSlider(fillindex,val){
  //sets the text display and location for each thumb and the slider fill
  let min = Number(sliders[fillindex].getAttribute("min"));
  let max = Number(sliders[fillindex].getAttribute("max"));
  let pc = (val/(max-min)) * 100
  setThumbText(slidervalues[fillindex],val,pc);
  setThumb(thumbs[fillindex],pc);
  setSliderFill(sliderfills[fillindex],pc);
}
function setThumbText(elem,val,pc){
  let size = getComputedStyle(elem).getPropertyValue("--thumbsize");
  let newx = `calc(${pc}% - ${parseInt(size)/2}px)`;
  elem.style.left = newx;
  elem.innerHTML = val;
}
function setThumb(elem,val){
  let size = getComputedStyle(elem).getPropertyValue("--thumbsize");
  let newx = `calc(${val}% - ${parseInt(size)/2}px)`;
  elem.style.left = newx;
  let max = 100;
  let degrees = 360 * (val/max);
  let rotation = `rotate(${degrees}deg)`;
	elem.style.transform = rotation;
}
function setSliderFill(elem,val){
  let fillcolor = getComputedStyle(elem).getPropertyValue("--accentcolor");
  let alphafillcolor = getComputedStyle(elem).getPropertyValue("--accentcoloralpha");
  // we create a linear gradient with a color stop based on the slider value
  let gradient = `linear-gradient(to right, ${fillcolor} 0%,
${alphafillcolor} ${val}%,
rgba(255,255,255,0.1) ${Number(val) + 1}%,
rgba(255,255,255,0)  100%)`;
  elem.style.backgroundImage = gradient;
}
