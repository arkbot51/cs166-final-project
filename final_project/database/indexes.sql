DROP INDEX IF EXISTS idx_auction_item;
DROP INDEX IF EXISTS idx_item_seller;
DROP INDEX IF EXISTS idx_auction_status;
DROP INDEX IF EXISTS idx_bid_buyer;
DROP INDEX IF EXISTS idx_bid_auction;

-- for joining items table and active auctions
create index idx_auction_item on auction(item_id);
create index idx_item_seller on item(seller_login);

-- for filtering active vs closed auctions
create index idx_auction_status on auction(auction_status);

-- for looking up bid history
create index idx_bid_buyer on bid(buyer_login);

-- for faster retrieval of bids 
CREATE INDEX idx_bid_auction ON bid(auction_id);