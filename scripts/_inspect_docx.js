const JSZip = require("jszip");
const fs = require("fs");

async function inspect(filename) {
  const data = fs.readFileSync(filename);
  const zip = await JSZip.loadAsync(data);
  console.log("\n=== " + filename + " ===");
  const files = Object.keys(zip.files).sort();
  for (const f of files) {
    const entry = zip.files[f];
    if (!entry.dir) {
      const content = await entry.async("nodebuffer");
      console.log("  " + f + " (" + content.length + " bytes)");
    }
  }

  // Check content_types
  const ct = await zip.file("[Content_Types].xml").async("text");
  console.log("\nContent_Types has png:", ct.includes("png"));
  console.log("Content_Types:", ct.substring(0, 800));

  // Check relationships
  const rels = await zip.file("word/_rels/document.xml.rels").async("text");
  console.log("\nRelationships:\n", rels);

  // Check document.xml for blip references
  const docXml = await zip.file("word/document.xml").async("text");
  const blips = docXml.match(/a:blip[^>]*/g) || [];
  console.log("\nBlip references:", blips);
}

async function main() {
  await inspect("_test_multi_img.docx");
  await inspect("BLOG_Sales_Commission_Odoo_19_V5.docx");
}

main().catch(e => console.error(e));
