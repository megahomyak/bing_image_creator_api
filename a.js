const start = async function () {

console.log("started!")

let bimg = await import("bimg");

let links = await bimg.generateImagesLinks("cute puppies")

console.log(links);
}

start()
