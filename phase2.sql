Create table Users (
    login varchar(50) primary key,
    password varchar(255) not null,
    phoneNum varchar(15) not null,
    role varchar(10) not null check (role in ('Buyer', 'Seller', 'Admin')),
    address text not null,
    favoriteCategory varchar(50)
);

Create table Items(
    itemID char(9) primary key,
    itemName varchar(255) not null,
    category varchar(50) not null,
    startingPrice decimal (10, 2) not null check (startingPrice >= 0),
    description text,
    condition varchar(50),
    imageURL text,
    sellerLogin varchar(50) not null,
    foreign key (sellerLogin) references Users(login) on delete cascade
);

Create table Auctions(
    auctionID char(9) primary key,
    itemID char(9) not null unique,
    currentHighestBid decimal(10,2) default 0.00,
    winnerLogin varchar(50),
    sellerLogin varchar(50) not null,
    auctionStatus varchar(10) not null check (auctionStatus in ('Active', 'Closed')),
    foreign key (itemID) references Items(itemID),
    foreign key (winnerLogin) references Users(login),
    foreign key (sellerLogin) references Users(login)
);

Create table Bids(
    bidID char(9) primary key,
    auctionID char(9) not null,
    bidderLogin varchar(50) not null,
    bidAmount decimal(10,2) not null check (bidAmount > 0),
    bidTimestamp timestamp default current_timestamp,
    foreign key (auctionID) references Auctions(auctionID),
    foreign key (bidderLogin) references Users(login)
);

Create table Payments (
    paymentID serial primary key,
    auctionID char(9) not null unique,
    buyerLogin varchar(50) not null,
    amount decimal(10,2) not null check (amount >=0),
    paymentStatus varchar(10) not null check (paymentStatus in ('Pending', 'Completed', 'Failed')),
    foreign key (auctionID) references Auctions(auctionID),
    foreign key (buyerLogin) references Users(login)
);

Create table Shipments(
    shipmentID char(9) primary key,
    auctionID char(9) not null unique,
    address text not null,
    shipmentStatus varchar(10) not null check (shipmentStatus in ('Pending', 'Shipped', 'Delivered')),
    trackingNumber varchar(100),
    foreign key (auctionID) references Auctions(auctionID)
);