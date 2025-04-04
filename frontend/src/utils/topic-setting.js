function getColor(topic) {
    if (topic === 'A') { // 红色
        return "#da7a73"
    } else if (topic === 'B') { // 橙色
        return "#ffb67a"
    } else if (topic === 'C') { // 绿色
        return "#9ee292"
    } else if (topic === 'D') { // 蓝色
        return "#7ab5ff"
    } else { // 紫色
        return "#DDA0DD"
    }
}

function getDarkColor(topic) {
    if (topic === 'A') { // 红色
        return "#693b38"
    } else if (topic === 'B') { // 橙色
        return "#684a32"
    } else if (topic === 'C') { // 绿色
        return "#43613e"
    } else if (topic === 'D') { // 蓝色
        return "#334a68"
    } else { // 紫色
        return "#5e455e"
    }
}

function getUrl(topic) {
    if (topic === 'A') { // 红色
        return "https://fastly.picsum.photos/id/859/1919/1919.jpg?hmac=24AoHo7Jc5TRRRaJfWO0B4z2wW5Jl14r56rVKeMfpZI"
    } else if (topic === 'B') { // 橙色
        return "https://fastly.picsum.photos/id/360/1925/1280.jpg?hmac=vX9T-qgnqfOUqLnxlsxCZfkKn_wi-9vtPKdbq7H6EgU"
    } else if (topic === 'C') { // 绿色
        return "https://fastly.picsum.photos/id/509/4608/3456.jpg?hmac=ZvNo59d3NP2XjQE75AaROWBTpW2BAzZgWb0-Jso0l9Y"
    } else if (topic === 'D') { // 蓝色
        return "https://fastly.picsum.photos/id/53/1280/1280.jpg?hmac=QP5opo-oENp5iFwsSiWH8azQuR0w0bwps6MT6yvhKwA"
    } else { // 紫色
        return "https://fastly.picsum.photos/id/723/5000/3333.jpg?hmac=Lq_OA9h0W8RDhE3xt44qzGv5PtQVLSnVCjoizkIiQNs"
    }
}

function getRadialGradient(topic) {
    return 'background: radial-gradient(circle, rgba(255, 255, 255, 1), ' + getColor(topic) + '88)'
}

function getLinearGradient(topic) {
    return 'background: linear-gradient(90deg, rgba(255, 255, 255, 1), ' + getColor(topic) + '88)'
}

function getLinearGradientLiteral(topic) {
    return 'background: linear-gradient(90deg, rgba(255, 255, 255, 1), ' + getColor(topic) + '88)'
}

export default {
    getDarkColor,
    getColor,
    getUrl,
    getRadialGradient,
    getLinearGradient,
    getLinearGradientLiteral
}