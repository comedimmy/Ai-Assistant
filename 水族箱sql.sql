DROP database IF EXISTS `Test`;

CREATE Database Test;

use Test;

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `UserID` INTEGER NOT NULL AUTO_INCREMENT,
  `UserName` nvarchar(128) NOT NULL UNIQUE,
  `LoginType` ENUM("Line","Google") NOT NULL,
  `LastLoginTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,      -- 最後登入時間
  PRIMARY KEY (`userid`)
);

DROP TABLE IF EXISTS `Aquarium`;

CREATE TABLE `Aquarium` (
  `AquariumID` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `UserID` INTEGER NOT NULL,
  `AquariumName` nvarchar(128) NOT NULL,
  `MaxTemperature` INTEGER NOT NULL,
  `MixTemperature` INTEGER NOT NULL,
  `FishType` ENUM("A","B","C") NOT NULL,
  `FishNumber` INTEGER NOT NULL,
  `FeedSize` float NOT NULL,
  `FeedTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `WaterLine` float NOT NULL,
  `AiModle` ENUM("A","B","C") NOT NULL, 
  
  `LightIngType` ENUM("0","1") NOT NULL,
  `TDSIng` float NOT NULL,
  `Temperature` float NOT NULL
);

DROP TABLE IF EXISTS `MsgLogs`;

CREATE TABLE `MsgLogs` (
  `LogID` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `AquariumID` INTEGER NOT NULL,
  `Message` nvarchar(2048) NOT NULL,
  `UserType` ENUM("User","Ai") NOT NULL,
  `LogTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 資料更新時
  FOREIGN KEY (AquariumID) REFERENCES Aquarium(AquariumID)
);

DROP TABLE IF EXISTS `ValuesLog`;

CREATE TABLE `ValuesLog` (
  `LogID` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `AquariumID` INTEGER NOT NULL,
  `LightType` ENUM("0","1") NOT NULL,
  `TDS` float NOT NULL,
  `Temperature` float NOT NULL,
  `LogTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 資料更新時間
  FOREIGN KEY (AquariumID) REFERENCES Aquarium(AquariumID)
);

DROP TABLE IF EXISTS `ActionLog`;

CREATE TABLE `ActionLog` (
  `AquariumID` INTEGER NOT NULL,
  `LogID` INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `LogType` ENUM("Action","Success","Error","ValueError") NOT NULL,
  `ActionType` ENUM("01","02","03","04") NOT NULL, --類型
  `ActionValue` Varchar(64) NOT NULL,
  `LogTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 資料更新時間
  FOREIGN KEY (AquariumID) REFERENCES Aquarium(AquariumID)
);

DROP TABLE IF EXISTS `Photo`;

CREATE TABLE `Photo` (
  `AquariumID` INTEGER NOT NULL,
  `URL` Varchar(2048) NOT NULL,
  `LogTime` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (AquariumID) REFERENCES Aquarium(AquariumID)
);
