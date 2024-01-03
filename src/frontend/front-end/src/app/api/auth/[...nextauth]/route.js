import { connectMongoDB } from "../../../../../lib/mongodb";
import User from "../../../../../models/users";
import NextAuth from "next-auth/next";
import CredentialsProvider from "next-auth/providers/credentials";
import bcrypt from "bcrypt";
import { v4 as uuidv4 } from 'uuid';

function generateSessionId() {
  return uuidv4();
}

export const authOptions = {
    providers: [
      CredentialsProvider({
        name: "credentials",
        credentials: {
          // username: { label: 'Username', type: 'text' },
          // password: {  label: 'Password', type: 'password' }
        },
        async authorize(credentials, req)  {
          const email = credentials.email;
          const password = credentials.password;
          try {
            const db = await connectMongoDB();
            const user = await User.findOne({ email });

            if (!user) {
              return null; // Return null when user is not found
            }
            const passwordsMatch = await bcrypt.compare(password, user.password);
  
            if (!passwordsMatch) {
                console.log("Passwords did not match");
              return null; // Return null when passwords do not match
            }

            let sessionId = user.sessionId;
            if (!sessionId) {
              sessionId = generateSessionId();
            }

            // Return the user object when authentication is successful
            return {...user.toObject(), sessionId };

          } catch (error) {
            console.log("Error: ", error);
            return null; // Return null in case of an error
          }
        },
      }),
    ],
    callbacks: {
      async jwt({ token, user }) {
        if (user?._id) {
          token._id = user._id;
          // store sessionId in token
          if (user.sessionId) {
            token.sessionId = user.sessionId;
          }
        }
        console.log(token)
        return token;
      },
      // async jwt({token, user}) {
      //   if (user) {
      //     token.email = user.email;
      //   }
      //   console.log(token);
      //   return token;
      // },
      async session({ session, token}) {
        if (session.user) {
          const user = await User.findOne({ email: session.user.email });
          // session.user = user;
          session.user = user.name; // Update the session user object
          session.email = user.email;
          session._id = user.id;
          session.sessionId = token.sessionId;
        }
        // user _id which matches mongoDB id
        // 25d043a4f8f94aa5a3488bb481369291
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