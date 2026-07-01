-- Admin monitoring schema reference.
-- SQLAlchemy creates these tables automatically at startup; this file documents
-- the equivalent migration for deployments that prefer explicit DDL review.

CREATE TABLE IF NOT EXISTS admin_users (
  id VARCHAR(36) PRIMARY KEY,
  email VARCHAR(320) NOT NULL UNIQUE,
  display_name VARCHAR(160) NOT NULL,
  role VARCHAR(32) NOT NULL,
  password_hash TEXT NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL,
  last_login_at TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS ix_admin_users_email ON admin_users (email);
CREATE INDEX IF NOT EXISTS ix_admin_users_role ON admin_users (role);

CREATE TABLE IF NOT EXISTS admin_chatbot_permissions (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL,
  chatbot_key VARCHAR(96) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  CONSTRAINT uq_admin_chatbot_permission UNIQUE (user_id, chatbot_key),
  CONSTRAINT fk_admin_chatbot_permissions_user
    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_admin_chatbot_permissions_user_chatbot
  ON admin_chatbot_permissions (user_id, chatbot_key);

CREATE TABLE IF NOT EXISTS admin_audit_logs (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NULL,
  action VARCHAR(64) NOT NULL,
  resource_type VARCHAR(64) NULL,
  resource_id VARCHAR(128) NULL,
  created_at TIMESTAMP NOT NULL,
  metadata_json TEXT NULL,
  CONSTRAINT fk_admin_audit_logs_user
    FOREIGN KEY (user_id) REFERENCES admin_users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_user_id ON admin_audit_logs (user_id);
CREATE INDEX IF NOT EXISTS ix_admin_audit_logs_action ON admin_audit_logs (action);

CREATE TABLE IF NOT EXISTS backend_request_logs (
  id VARCHAR(36) PRIMARY KEY,
  conversation_id VARCHAR(36) NULL,
  message_id VARCHAR(36) NULL,
  client_message_id VARCHAR(64) NULL,
  participant_key VARCHAR(320) NULL,
  step VARCHAR(64) NOT NULL,
  status VARCHAR(24) NOT NULL,
  detail TEXT NULL,
  created_at TIMESTAMP NOT NULL,
  metadata_json TEXT NULL,
  CONSTRAINT fk_backend_request_logs_conversation
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
  CONSTRAINT fk_backend_request_logs_message
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_backend_request_logs_conversation_id ON backend_request_logs (conversation_id);
CREATE INDEX IF NOT EXISTS ix_backend_request_logs_message_id ON backend_request_logs (message_id);
CREATE INDEX IF NOT EXISTS ix_backend_request_logs_client_message ON backend_request_logs (client_message_id);
CREATE INDEX IF NOT EXISTS ix_backend_request_logs_participant_key ON backend_request_logs (participant_key);
CREATE INDEX IF NOT EXISTS ix_backend_request_logs_step ON backend_request_logs (step);
CREATE INDEX IF NOT EXISTS ix_backend_request_logs_status ON backend_request_logs (status);
CREATE INDEX IF NOT EXISTS ix_backend_request_logs_conversation_created
  ON backend_request_logs (conversation_id, created_at);
