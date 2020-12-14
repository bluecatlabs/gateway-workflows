// Copyright 2020 BlueCat Networks. All rights reserved.
// JavaScript for your page goes in here.
content_box = $("#data_display")
for (var ip in content) {
    console.log(ip)
    records = ""
    for (var record in content[ip]) {
        records += content[ip][record] + " "
    }
    content_box.append("<p>"+ip + " | " + records+"</p>")

}