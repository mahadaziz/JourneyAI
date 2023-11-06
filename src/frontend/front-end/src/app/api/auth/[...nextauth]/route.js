import { connectMongoDB } from "../../../../../lib/mongodb";
import User from "../../../../../models/users";
import NextAuth from "next-auth/next";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcrypt";

export const authOptions = {
    providers: [
      CredentialsProvider({
        name: "credentials",
        credentials: {
          // username: { label: 'Username', type: 'text' },
          // password: {  label: 'Password', type: 'password' }
        },
        async authorize(credentials, req)  {
        //   const email = credentials.email;
          const username = credentials.username
          const password = credentials.password;
          try {
            const db = await connectMongoDB();
            // const user = await User.findOne({ email });
            const user = await User.findOne({ username });

            console.log("this is the user", user);
            if (!user) {
              return null; // Return null when user is not found
            }
            // const passwordsMatch = await bcrypt.compare(password, user.password);
  
            if (!(password == user.password)) {
                console.log("Passwords did not match");
              return null; // Return null when passwords do not match
            }
            // Return the user object when authentication is successful
            return user;

          } catch (error) {
            console.log("Error: ", error);
            return null; // Return null in case of an error
          }
        },
      }),
    ],
    callbacks: {
      async jwt({token, user}) {
        if (user) {
          token.username = user.username;
        }
        return token;
      },
      async session({ session}) {
        if (session.user) {
            const user = await User.findOne({ username: session.user.username });
            session.user = user; // Update the session user object
        //   session.user.test = user.test;
        }
        return session;
      }
    },
    secret: process.env.NEXTAUTH_SECRET,
    session: {
      strategy: "jwt",
    },
    pages: {
      signIn: "/login",
    },
  };
  
  const handler = NextAuth(authOptions);
  
  export { handler as GET, handler as POST };