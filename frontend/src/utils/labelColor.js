function getLabelColor(label) {
  switch (label) {
    case 'BUG':
      return '#ff0000'
    case 'ENHANCEMENT':
      return '#ffa500'
    case 'FEATURE':
      return '#86eb34'
    case 'DUPLICATE':
      return '#8d8d8d'
    case 'QUESTION' :
      return '#08E6C0'
  }
}

export default getLabelColor