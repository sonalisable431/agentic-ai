const path = require("path");
const ForkTsCheckerWebpackPlugin = require("fork-ts-checker-webpack-plugin");

module.exports = {
  mode: "production",
  entry: {
    index: './src/index.ts'
  },
  resolve: {
    extensions: [".js", ".jsx", ".json", ".ts", ".tsx"],
  },
  output: {
    libraryTarget: "commonjs",
    path: path.join(__dirname, "dist"),
    filename: "[name].js",
  },
  target: "node",
  module: {
    rules: [
      {
        // Include ts, tsx, js, and jsx files.
        test: /\.(ts|js)x?$/,
        exclude: /node_modules/,
        use: [
          "babel-loader"
        ],
      }
    ],
  },
  plugins: [new ForkTsCheckerWebpackPlugin()],
  externals: ['edl_common_layer', 'esi-common-layer']
}