DROP INDEX IF EXISTS idx_auction_item;
DROP INDEX IF EXISTS idx_item_seller;
DROP INDEX IF EXISTS idx_auction_status;
DROP INDEX IF EXISTS idx_bid_buyer;
DROP INDEX IF EXISTS idx_bid_auction;

-- for joining items table and active auctions
CREATE INDEX idx_auction_item ON auction(item_id);
CREATE INDEX idx_item_seller ON item(seller_login);

-- for filtering active vs closed auctions
CREATE INDEX idx_auction_status ON auction(auction_status);

-- for looking up bid history
CREATE INDEX idx_bid_buyer ON bid(buyer_login);

-- for faster retrieval of bids  
CREATE INDEX idx_bid_auction ON bid(auction_id);