const fs = require('fs')
const path = require('path')

// Limpar dist
const distPath = path.join(__dirname, 'dist')
if (fs.existsSync(distPath)) {
  fs.rmSync(distPath, { recursive: true, force: true })
  console.log('✅ Pasta dist removida')
}

// Atualizar package.json para forçar rebuild
const packagePath = path.join(__dirname, 'package.json')
const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'))
pkg.version = Date.now().toString()
fs.writeFileSync(packagePath, JSON.stringify(pkg, null, 2))
console.log('✅ Versão atualizada para forçar rebuild')

console.log('🚀 Execute: npm run build && npm run deploy')