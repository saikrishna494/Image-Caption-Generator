let multiLine=`
gjskfjg
sdkg;jg
dfjlhadg
adfkjgj
adgjjhg`;
console.log(multiLine)
const result = [];
const drone = {
    speed: 100,
    color: 'yellow'
}
const droneKeys = Object.keys(drone);
droneKeys.forEach( function(key) {
    result.push(key+': '+drone[key])
})
console.log(result)
const meal = ["soup", "steak", "ice cream"]
    let [starter] = meal;
    console.log(starter);