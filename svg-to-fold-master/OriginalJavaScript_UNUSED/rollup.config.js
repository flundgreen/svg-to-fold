import { string } from "rollup-plugin-string";
import cleanup from "rollup-plugin-cleanup";
import babel from "rollup-plugin-babel";
import minify from "rollup-plugin-babel-minify";

const format = "umd";
const banner = `/* convert images into FOLD file format.
more info at https://github.com/robbykraft/tofold
more info on the FOLD format https://github.com/edemaine/fold
(c) Robby Kraft, MIT License */
`;

module.exports = [{
  input: "src/index.js",
  output: {
    name: "tofold",
    file: "tofold.js",
    format,
    banner,
  },
  plugins: [
    cleanup({
      comments: "none",
      maxEmptyLines: 0,
    }),
    babel({
      babelrc: false,
      presets: [["@babel/env", { modules: false }]],
    }),
    string({
      include: "**/*.css", // allows .css files to be imported as a module
    }),
  ],
},
{
  input: "src/index.js",
  output: {
    name: "tofold",
    file: "tofold.min.js",
    format,
    banner,
  },
  plugins: [
    cleanup({ comments: "none" }),
    babel({
      babelrc: false,
      presets: [["@babel/env", { modules: false }]],
    }),
    minify({ mangle: { names: false } }),
    string({
      include: "**/*.css", // allows .css files to be imported as a module
    }),
  ],
}];
