psql <<EOF
CREATE DATABASE "flask" WITH OWNER="postgres" TEMPLATE=template0 ENCODING='UTF8';
EOF

psql <<EOF
CREATE DATABASE "bbmaster" WITH OWNER="postgres" TEMPLATE=template0 ENCODING='UTF8';
EOF
