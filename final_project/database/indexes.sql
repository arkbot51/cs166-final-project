-- for joining items table and active auctions
create index idx_auction_item on auction(item_id);
create index idx_item_seller on item(seller_login);

-- for filtering active vs closed auctions
create index idx_auction_status on auction(auction_status);

-- for looking up bid history
create index idx_bid_buyer on bid(buyer_login);
