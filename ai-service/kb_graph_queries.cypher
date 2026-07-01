// ============================================================
// 1) OVERVIEW: show a rich mixed subgraph
// ============================================================
MATCH (u:User)-[:HAS_SESSION]->(s:Session)<-[:IN_SESSION]-(e:Event)-[:ON_PRODUCT]->(p:Product)
MATCH (e)-[:OF_TYPE]->(a:ActionType)
MATCH (e)-[:ON_DAY]->(d:Day)
WITH u, s, e, p, a, d
LIMIT 300
RETURN u, s, e, p, a, d;


// ============================================================
// 2) USER JOURNEY: sequence timeline for a specific user
// ============================================================
MATCH (u:User {user_id: 42})-[:PERFORMED]->(e:Event)
OPTIONAL MATCH (e)-[:NEXT]->(e2:Event)
OPTIONAL MATCH (e)-[:ON_PRODUCT]->(p:Product)
OPTIONAL MATCH (e)-[:OF_TYPE]->(a:ActionType)
RETURN u, e, e2, p, a
ORDER BY e.timestamp;


// ============================================================
// 3) ACTION TRANSITION GRAPH (global behavior dynamics)
// ============================================================
MATCH (a1:ActionType)-[r:TRANSITIONS_TO]->(a2:ActionType)
RETURN a1, r, a2
ORDER BY r.count DESC;


// ============================================================
// 4) HOT PRODUCTS by aggregated preference score
// ============================================================
MATCH (:User)-[r:INTERACTED_WITH]->(p:Product)
WITH p,
     sum(r.preference_score) AS popularity,
     sum(r.cart_count) AS carts,
     sum(r.click_count) AS clicks,
     sum(r.view_count) AS views
ORDER BY popularity DESC
LIMIT 25
RETURN p.product_id AS product_id, popularity, carts, clicks, views;


// ============================================================
// 5) PRODUCT FLOW NETWORK (what product often leads to what)
// ============================================================
MATCH (p1:Product)-[r:NEXT_PRODUCT]->(p2:Product)
WHERE r.count >= 3
RETURN p1, r, p2
ORDER BY r.count DESC
LIMIT 200;


// ============================================================
// 6) USER SIMILARITY CLUSTERS
// ============================================================
MATCH (u1:User)-[r:SIMILAR_TO]->(u2:User)
WHERE r.jaccard >= 0.25
RETURN u1, r, u2
ORDER BY r.jaccard DESC
LIMIT 200;


// ============================================================
// 7) SESSION INTENSITY MAP
// ============================================================
MATCH (u:User)-[:HAS_SESSION]->(s:Session)<-[:IN_SESSION]-(e:Event)
WITH u, s, count(e) AS events_in_session, sum(e.weight) AS intensity
ORDER BY intensity DESC
LIMIT 100
RETURN u.user_id AS user_id, s.session_id AS session_id, events_in_session, intensity;


// ============================================================
// 8) TEMPORAL HEAT by day + hour bucket
// ============================================================
MATCH (e:Event)-[:ON_DAY]->(d:Day)
MATCH (e)-[:IN_HOUR]->(h:HourBucket)
WITH d.date AS date, d.day_name AS day_name, h.name AS hour_bucket, count(e) AS event_count
ORDER BY date, hour_bucket
RETURN date, day_name, hour_bucket, event_count;


// ============================================================
// 9) CART-CONVERSION CHAINS (view -> click -> add_to_cart)
// ============================================================
MATCH (e1:Event)-[:OF_TYPE]->(:ActionType {name: 'view'})
MATCH (e1)-[:NEXT]->(e2:Event)-[:OF_TYPE]->(:ActionType {name: 'click'})
MATCH (e2)-[:NEXT]->(e3:Event)-[:OF_TYPE]->(:ActionType {name: 'add_to_cart'})
MATCH (u:User)-[:PERFORMED]->(e1)
RETURN u, e1, e2, e3
LIMIT 100;


// ============================================================
// 10) BEAUTY SHOWCASE: colorful star around top users
// ============================================================
MATCH (u:User)-[:PERFORMED]->(e:Event)-[:ON_PRODUCT]->(p:Product)
WITH u, count(e) AS interactions
ORDER BY interactions DESC
LIMIT 10
MATCH (u)-[:PERFORMED]->(e:Event)-[:ON_PRODUCT]->(p:Product)
MATCH (e)-[:OF_TYPE]->(a:ActionType)
RETURN u, e, p, a;
