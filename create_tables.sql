
CREATE DATABASE IF NOT EXISTS my_ad_data;
USE my_ad_data;
-- Advertisers
-- Зберігає юнік інформацію про кожного рекламодавця
-- Це усуває дублювання AdvertiserName у таблицях Campaigns та ad_events
CREATE TABLE Advertisers (
    AdvertiserID INT AUTO_INCREMENT PRIMARY KEY,
    AdvertiserName VARCHAR(255) UNIQUE NOT NULL
);

-- Campaigns
-- Зберігає деталі кожної рекламної кампанії
-- Відокремлення інформації про кампанії дозволяє уникнути повторення CampaignName
-- CampaignStartDate, CampaignEndDate, TargetingCriteria, AdSlotSize, Budget
-- для кожного показу в таблиці ad_events
CREATE TABLE Campaigns (
    CampaignID INT AUTO_INCREMENT PRIMARY KEY,
    AdvertiserID INT NOT NULL,
    CampaignName VARCHAR(255) NOT NULL,
    CampaignStartDate DATE NOT NULL,
    CampaignEndDate DATE NOT NULL,
    TargetingCriteria TEXT,
    AdSlotSize VARCHAR(50),
    Budget DECIMAL(10, 2) NOT NULL,
    RemainingBudget DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (AdvertiserID) REFERENCES Advertisers(AdvertiserID)
);

-- Users
-- Зберігає юнік інформацію про кожного користувача.
-- Це централізована таблиця для даних користувачів, що усуває дублювання
-- Age, Gender, Location, SignupDate
CREATE TABLE Users (
    UserID INT PRIMARY KEY, -- UserID вже унікальний в наборі даних
    Age INT,
    Gender VARCHAR(50),
    Location VARCHAR(255),
    SignupDate DATE
);

-- Interests
-- Зберігає список юнік інтересів.
-- Це нормалізує поле Interests з таблиці Users, яке було багатозначним
CREATE TABLE Interests (
    InterestID INT AUTO_INCREMENT PRIMARY KEY,
    InterestName VARCHAR(255) UNIQUE NOT NULL
);

-- UserInterests
-- Створює зв'язок мені ту мені між користувачами та інтересами
-- Дозволяє одному користувачеві мати багато інтересів і один інтерес
-- бути пов'язаним з багатьма користувачами
CREATE TABLE UserInterests (
    UserID INT NOT NULL,
    InterestID INT NOT NULL,
    PRIMARY KEY (UserID, InterestID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID),
    FOREIGN KEY (InterestID) REFERENCES Interests(InterestID)
);

-- Impressions
-- Зберігає кожен показ реклами.
-- Містить інформацію про те, коли і де відбувся показ, хто його бачив,
-- до якої кампанії він належить, а також витрати, пов'язані з показом.
-- EventID  стане ImpressionID.
CREATE TABLE Impressions (
    ImpressionID VARCHAR(36) PRIMARY KEY, -- EventID 
    CampaignID INT NOT NULL,
    UserID INT NOT NULL,
    Device VARCHAR(50),
    Location VARCHAR(255), -- Локація, де відбувся показ
    Timestamp DATETIME NOT NULL,
    BidAmount DECIMAL(10, 2),
    AdCost DECIMAL(10, 2),
    FOREIGN KEY (CampaignID) REFERENCES Campaigns(CampaignID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Clicks
-- Зберігає інформацію лише про кліки
-- Це вирішує проблему NULL-значень у WasClicked, ClickTimestamp та AdRevenue
-- для показів, які не призвели до кліків 
-- Зв'язок один до одного з Impressions
-- забезпечує, що кожен клік пов'язаний з унікальним показом
CREATE TABLE Clicks (
    ClickID INT AUTO_INCREMENT PRIMARY KEY,
    ImpressionID VARCHAR(36) UNIQUE NOT NULL, -- UNIQUE для забезпечення зв'язку 1:1 з Impressions
    ClickTimestamp DATETIME NOT NULL,
    AdRevenue DECIMAL(10, 2),
    FOREIGN KEY (ImpressionID) REFERENCES Impressions(ImpressionID)
);