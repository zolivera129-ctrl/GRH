import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

const faces: [string, string, string][] = [
  ["Raleway", "raleway-latin-300-normal", "300"],
  ["Raleway", "raleway-latin-400-normal", "400"],
  ["Raleway", "raleway-latin-500-normal", "500"],
  ["Raleway", "raleway-latin-600-normal", "600"],
  ["Raleway", "raleway-latin-700-normal", "700"],
  ["Raleway", "raleway-latin-800-normal", "800"],
  ["Raleway", "raleway-latin-900-normal", "900"],
  ["Open Sans", "open-sans-latin-400-normal", "400"],
  ["Open Sans", "open-sans-latin-600-normal", "600"],
  ["Open Sans", "open-sans-latin-700-normal", "700"],
  ["Oswald", "oswald-latin-400-normal", "400"],
  ["Oswald", "oswald-latin-500-normal", "500"],
  ["Oswald", "oswald-latin-600-normal", "600"],
  ["Oswald", "oswald-latin-700-normal", "700"],
  ["Inter", "inter-latin-400-normal", "400"],
  ["Inter", "inter-latin-500-normal", "500"],
  ["Inter", "inter-latin-600-normal", "600"],
  ["Inter", "inter-latin-700-normal", "700"],
];

export const fontsReady = Promise.all(
  faces.map(([family, file, weight]) =>
    loadFont({ family, url: staticFile(`fonts/${file}.woff2`), weight }),
  ),
);
