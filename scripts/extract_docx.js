const mammoth = require("mammoth");
const fs = require("fs");

const filePath = process.argv[2];

mammoth.extractRawText({path: filePath})
    .then(function(result){
        fs.writeFileSync("temp_extract.txt", result.value);
        console.log("Extraction complete.");
    })
    .catch(function(err){
        console.error("Error:", err);
    });
