import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";
import { FONT_FAMILY } from "./config";

// Inter (SIL Open Font License), servida localmente a partir de public/fonts.
for (const weight of ["400", "500", "600", "700"]) {
  loadFont({
    family: FONT_FAMILY,
    url: staticFile(`fonts/inter-latin-${weight}-normal.woff2`),
    weight,
  });
}
