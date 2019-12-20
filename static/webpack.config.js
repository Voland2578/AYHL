// aside from [name], there is [hash] and some other variables we can use
const HtmlWebPackPlugin = require('html-webpack-plugin')
const webpack = require('webpack');
const config = {
    // ensure dumping of source code in a friendly manner
    devtool: 'eval-source-map',
    entry: {
        adminEntry:  __dirname + '/src/admin.jsx',
        clientEntry:  __dirname + '/src/client.tsx'
    },
    module: {
      rules: [
      {
        test: /\.(js|jsx)$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/
      }
      ]
    }, 
    // figure out how to put admin into a different bundle
    output: {
        path: __dirname + '/public/clientapp',
        filename: '[name]_bundle.js',
    },
    // support tsx ( typescript with JSX tags) as well as regular ts
    // next step, we will remove .jsx since we will always use typescript
    resolve: {
        extensions: ['.js', '.jsx', '.ts','.tsx','.css']
    },
    
    // attempt to generate index.html using the client entry bundle only. 
    // will try both. Template is the html page where the <script> tags with the bundle will be injected.
    // Also, what in the hell is the "hash". I wonder if I need to provide it in the file names
    plugins: [
       new HtmlWebPackPlugin( { title: 'Client Entry', template: './src/clientapp_template.html', chunks:['clientEntry'] , filename: 'hockeystats.html'   })
    ]
};
module.exports = config;
// ensure that filename has [name] to emit 2 separate bundle files
