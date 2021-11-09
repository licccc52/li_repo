FROM mhart/alpine-node:12.14.1 as react-build
RUN mkdir /var/app
WORKDIR /var/app
COPY . ./
RUN yarn
RUN yarn build

FROM nginx
COPY --from=react-build /var/app/build /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;","-c","/etc/nginx/nginx.conf"]