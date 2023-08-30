// Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = [
    {
        entry: {
            roleMntPage: path.join(__dirname, 'src/pages/roleMntPage', 'index.js'),
        },
        output: {
            path: path.join(__dirname, '../'),
            publicPath: '',
            filename: 'js/[name].js',
            assetModuleFilename: 'img/[name][ext]',
        },
        mode: process.env.NODE_ENV || 'development',
        resolve: {
            modules: [path.resolve(__dirname, 'src'), 'node_modules'],
            alias: {
                react: 'preact/compat',
                'react-dom': 'preact/compat',
            },
        },
        devServer: {
            proxy: {
                '/': {
                    target: 'http://localhost:5000',
                },
            },
            static: path.join(__dirname, 'src'),
        },
        module: {
            rules: [
                {
                    test: /\.m?js$/,
                    resolve: {
                        fullySpecified: false,
                    },
                    exclude: /(node_modules|bower_components)/,
                    use: ['babel-loader'],
                },
                {
                    test: /\.(css|scss)$/,
                    use: ['style-loader', 'css-loader'],
                },
                {
                    test: /\.less$/,
                    use: [
                        'style-loader',
                        'css-loader',
                        {
                            loader: 'less-loader',
                        },
                    ],
                },
                {
                    test: /\.(svg|png)$/,
                    type: 'asset/resource',
                },
                {
                    test: /\.(woff|woff2)$/,
                    type: 'asset/resource',
                    generator: {
                        filename: 'fonts/[hash][ext]',
                    },
                },
            ],
        },
        plugins: [
            new HtmlWebpackPlugin({
                template: path.join(__dirname, 'src', 'index.html'),
                filename: 'roleMntPage/index.html',
                chunks: ['roleMntPage'],
            }),
        ],
    },
];
