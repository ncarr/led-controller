export default function (color) {
    return `rgba(${mixWhiteAndAlpha(color.red, color.white, color.opacity)}, ${mixWhiteAndAlpha(color.green, color.white, color.opacity)}, ${mixWhiteAndAlpha(color.blue, color.white, color.opacity)}, ${mixWhiteToAlpha(color.opacity, color.white)})`
}

function mixWhiteAndAlpha(channel, white, alpha) {
    return mixWhiteToChannel(channel, alpha) / mixWhiteToAlpha(alpha, white)
}

function mixWhiteToChannel(channel, white) {
    return white / 2 + channel * (1 - white / 255 / 2)
}

function mixWhiteToAlpha(alpha, white) {
    return white / 255 / 2 + alpha * (1 - white / 255 / 2)
}