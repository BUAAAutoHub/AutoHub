import { sha256 } from "js-sha256";
import Identicon from "identicon.js";

function getIdenticon(str, size, who) {
    let background = [255, 255, 255, 255]
    if (who === 'user') {
        background = [223, 223, 223, 223]
    } else if (who === 'proj') {
        background = [64, 64, 64, 255]
    }
    let hash = sha256(str)
    let data = new Identicon(hash, {size: size, background: background}).toString()
    let ret = 'data:image/png;base64,' + data
    return ret
}

export default getIdenticon