-- Create tweets table
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('review', 'approved', 'rejected', 'sent')),
    text_adjusted TEXT,
    version INTEGER DEFAULT 1,
    score INTEGER CHECK (score >= 1 AND score <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE
);

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_tweets_updated_at
    BEFORE UPDATE ON tweets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();