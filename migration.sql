CREATE TABLE feeds(
  `name` text,
  `url` text
);

CREATE TABLE feed_content(
  `feed_id` integer,
  `url` text,
  `title` text,
  `categories` text,
  `pub_date` datetime,
  `description` text
);