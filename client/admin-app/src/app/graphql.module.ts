import { NgModule } from '@angular/core';
import { HttpClientModule, HttpClient } from '@angular/common/http';
// Apollo
import { ApolloModule, Apollo } from 'apollo-angular';
import { HttpLinkModule, HttpLink } from 'apollo-angular-link-http';
import { WebSocketLink } from 'apollo-link-ws';
import { split } from 'apollo-link';
import { getMainDefinition } from 'apollo-utilities';
import { InMemoryCache } from 'apollo-cache-inmemory';

import { OperationDefinitionNode, FragmentDefinitionNode } from 'graphql';

const uriQueries = '/graphql'
const uriSubscriptions = 'ws://localhost:8000/subscriptions'

@NgModule({
    exports: [
      HttpClientModule,
      ApolloModule,
      HttpLinkModule
    ]
  })
  export class GraphQLModule {
    constructor(
      apollo: Apollo,
      private httpClient: HttpClient
    ) {
      const httpLink = new HttpLink(httpClient).create({
        uri: uriQueries
      });

      const subscriptionLink = new WebSocketLink({
        uri: uriSubscriptions,
        options: {
          reconnect: true,
          // connectionParams: {
          //   authToken: localStorage.getItem('token') || null
          // }
        }
      });

      const link = split(
        ({ query }) => {
          var isSubscription = false;
          const mainDefinition = getMainDefinition(query);
          if (mainDefinition.kind === 'OperationDefinition')
          {
            isSubscription = ((mainDefinition as OperationDefinitionNode).operation === 'subscription');
          }
          return isSubscription;
        },
        subscriptionLink,
        httpLink
      );

      // create Apollo
      apollo.create({
        link,
        cache: new InMemoryCache()
      });
      console.log("Apollo created");
    }
  }