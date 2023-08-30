// Copyright 2023 BlueCat Networks (USA) Inc. and its affiliates. All Rights Reserved.
module.exports = {
    presets: [
        [
            '@babel/env',
            {
                targets: { 'chrome': '81', 'firefox': '75', 'edge': '79' },
            },
        ],
        ['@babel/react', { runtime: 'automatic' }],
    ],
};
