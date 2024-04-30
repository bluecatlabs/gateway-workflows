// Copyright 2024 BlueCat Networks (USA) Inc. and its affiliates
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// By: BlueCat Networks
// Date: 2024-04-30
// Gateway Version: 24.2.0
// Description: Gateway workflow to demonstrate use of REST API v2 client.

// JavaScript for your page goes in here.
$(document).ready(function() {

});

const clearChildren = (dst) => {
    while (dst.lastChild) {
        dst.removeChild(dst.lastChild);
    }
};

fetch("/nav_zones/api/v1/configurations")
    .then((response) => response.json())
    .then((data) => {
        const dst = document.querySelector("#configurations");
        clearChildren(dst);
        data.forEach((item) => {
            const el = document.createElement("option");
            el.value = item.id;
            el.innerText = item.name;
            dst.appendChild(el);
        })
    });

document.querySelector("#configurations")
    .addEventListener("change", (e, x) => {
        const vs = document.querySelector("#views");
        const zs = document.querySelector("#zones");
        clearChildren(vs);
        clearChildren(zs);
        const pid = e.target.selectedOptions[0].value;
        console.log("Will retrieve views for configurations with ID " + pid);
        fetch("/nav_zones/api/v1/views/?parent_id=" + pid)
            .then((response) => response.json())
            .then((data) => {
                const dst = document.querySelector("#views");
                clearChildren(dst);
                data.forEach((item) => {
                    const el = document.createElement("option");
                    el.value = item.id;
                    el.innerText = item.name;
                    dst.appendChild(el);
                })
            });
    });

document.querySelector("#views")
    .addEventListener("change", (e, x) => {
        const zs = document.querySelector("#zones");
        clearChildren(zs);
        const pid = e.target.selectedOptions[0].value;
        console.log("Will retrieve zones for view with ID " + pid);
        fetch("/nav_zones/api/v1/zones/?parent_id=" + pid)
            .then((response) => response.json())
            .then((data) => {
                const dst = document.querySelector("#zones");
                clearChildren(dst);
                data.forEach((item) => {
                    const el = document.createElement("option");
                    el.value = item.id;
                    el.innerText = item.name;
                    dst.appendChild(el);
                })
            });
    });
