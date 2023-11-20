## 📌 Description
create a standard waterfall chart between two datasets
## 📸 Screenshot
![screenshot1](https://github.com/pemn/assets/blob/main/db_waterfall1.png?raw=true)
## 📝 Parameters
name|optional|description
---|---|------
input_a,input_b|❎|path to data in a supported format
groups_a,groups_b|❎|group fields for comparison
value_a,value_b|❎|numeric field for totals
condition|☑️|only rows that evaluate to true will be used
output|☑️|path to save the buildup chart as either a xlsx workbook or a png image
display||show the result in a popup window

## 📓 Notes
 - The data must already be aggregated (each combination of groups only has one value)
 
## 📚 Examples
![screenshot1](https://github.com/pemn/assets/blob/main/db_waterfall2.png?raw=true)
## 🧩 Compatibility
distribution|status
---|---
![winpython_icon](https://github.com/pemn/assets/blob/main/winpython_icon.png?raw=true)|✔
![vulcan_icon](https://github.com/pemn/assets/blob/main/vulcan_icon.png?raw=true)|✔
![anaconda_icon](https://github.com/pemn/assets/blob/main/anaconda_icon.png?raw=true)|❌
## 🙋 Support
Any question or problem contact:
 - paulo.ernesto
## 💎 License
Apache 2.0
Copyright ![vale_logo_only](https://github.com/pemn/assets/blob/main/vale_logo_only_r.svg?raw=true) Vale 2023
