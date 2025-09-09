const a = require("./all_uvl-labtests_concepts.json");
const fs = require("fs");

external_ids = a.map((c) => c.external_id);

concepts = Object.fromEntries(a.map((c) => [c.display_name.toLowerCase(), c]));

concepts_to_check = require("./concepts-to-check.json");

missing = concepts_to_check.filter((c) => !concepts[c.toLowerCase()]);

fs.writeFileSync("./missing.json", JSON.stringify(missing, null, 2));
fs.writeFileSync("./external_ids.json", JSON.stringify(external_ids, null, 2));
