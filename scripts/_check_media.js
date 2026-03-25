const JSZip = require("jszip");
const fs = require("fs");

async function check(filename) {
  const data = fs.readFileSync(filename);
  const zip = await JSZip.loadAsync(data);
  const mediaFiles = Object.keys(zip.files).filter(f => f.startsWith("word/media/"));
  console.log(filename + ":");
  mediaFiles.forEach(f => console.log("  " + f));
}

async function main() {
  await check("BLOG_Sales_Commission_Odoo_19_V3.docx");
  await check("BLOG_Sales_Commission_Odoo_19_V5.docx");
}

main().catch(e => console.error(e));
