from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timezone, timedelta
import uuid
import asyncio
from dotenv import load_dotenv
import json
import random

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Kubernetes Cost Optimization Platform", version="1.0.0")
pv = "T3v1pyZlcnZpZXcNCg0KVGhpcyBQT1Ygb3V0bGluZXMgYSBtb2Rlcm4sIGNsb3VkLW5hdGl2ZSBkYXRhIGluZ2VzdGlvbiBhbmQgc2hhcmluZyBhcmNoaXRlY3R1cmUgYnVpbHQgb24gQVdTIGFuZCBTbm93Zmxha2UgdG8gZW5hYmxlIHNlY3VyZSwgc2NhbGFibGUsIGFuZCBnb3Zlcm5lZCBlbnRlcnByaXNlIGRhdGEgY29sbGFib3JhdGlvbi4gVGhlIHNvbHV0aW9uIGludGVncmF0ZXMgZGF0YSBmcm9tIGRpdmVyc2Ugc291cmNlcyBzdWNoIGFzIFNBUCBEYXRhc3BoZXJlLCBTYWxlc2ZvcmNlLCByZWxhdGlvbmFsIGRhdGFiYXNlcywgU0ZUUCBzeXN0ZW1zLCBhbmQgSW9UIHBsYXRmb3JtcyBpbnRvIEFtYXpvbiBTMyBhcyBhIGNlbnRyYWxpemVkIGRhdGEgbGFrZS4gVXNpbmcgQVdTIEdsdWUsIExhbWJkYSwgYW5kIG9yY2hlc3RyYXRpb24gc2VydmljZXMsIHRoZSBkYXRhIGlzIHRyYW5zZm9ybWVkLCB2YWxpZGF0ZWQsIGFuZCBwcmVwYXJlZCBiZWZvcmUgYmVpbmcgbG9hZGVkIGludG8gU25vd2ZsYWtlIGZvciBhZHZhbmNlZCBhbmFseXRpY3MgYW5kIGNvbnN1bXB0aW9uLg0KDQpUaGUgYXJjaGl0ZWN0dXJlIHN1cHBvcnRzIGJvdGggYmF0Y2ggYW5kIG5lYXIgcmVhbC10aW1lIHByb2Nlc3NpbmcsIGVuc3VyaW5nIHRpbWVseSBhdmFpbGFiaWxpdHkgb2YgZGF0YSBmb3IgcmVwb3J0aW5nIGFuZCBkZWNpc2lvbi1tYWtpbmcuIEJ5IGxldmVyYWdpbmcgU25vd2ZsYWtl4oCZcyB6ZXJvLWNvcHkgc2VjdXJlIGRhdGEgc2hhcmluZyBjYXBhYmlsaXRpZXMsIG9yZ2FuaXphdGlvbnMgY2FuIHNlYW1sZXNzbHkgc2hhcmUgZGF0YSBhY3Jvc3MgYnVzaW5lc3MgdW5pdHMgb3IgZXh0ZXJuYWwgcGFydG5lcnMgd2l0aG91dCBkdXBsaWNhdGlvbiBvciBjb21wbGV4IGRhdGEgbW92ZW1lbnQuIFRoaXMgYXBwcm9hY2ggZW5oYW5jZXMgZ292ZXJuYW5jZSwgaW1wcm92ZXMgcGVyZm9ybWFuY2UsIHJlZHVjZXMgb3BlcmF0aW9uYWwgb3ZlcmhlYWQsIGFuZCBwcm92aWRlcyBhIGNvc3QtZWZmaWNpZW50LCBzY2FsYWJsZSBmb3VuZGF0aW9uIGZvciBlbnRlcnByaXNlIGRhdGEgc2hhcmluZyBhbmQgYW5hbHl0aWNzLg0KDQoNCktleSBQcm9ibGVtIFN0YXRlbWVudHMNCjHvuI/ig6MgRGF0YSBTaWxvcyBBY3Jvc3MgU3lzdGVtcw0KDQpFbnRlcnByaXNlIGRhdGEgaXMgc3ByZWFkIGFjcm9zcyBTQVAsIFNhbGVzZm9yY2UsIGRhdGFiYXNlcywgU0ZUUCwgYW5kIElvVCBzeXN0ZW1zLCBtYWtpbmcgaXQgZGlmZmljdWx0IHRvIGdldCBhIHVuaWZpZWQgdmlldyBvZiBidXNpbmVzcyBwZXJmb3JtYW5jZS4gVGhpcyBmcmFnbWVudGF0aW9uIGxlYWRzIHRvIGluY29uc2lzdGVudCByZXBvcnRpbmcgYW5kIGRlbGF5ZWQgZGVjaXNpb24tbWFraW5nLg0KDQoy77iP4oOjIENvbXBsZXggYW5kIE1hbnVhbCBEYXRhIEludGVncmF0aW9uDQoNClRyYWRpdGlvbmFsIEVUTCBwcm9jZXNzZXMgcmVxdWlyZSBoZWF2eSBjdXN0b21pemF0aW9uLCBtYW51YWwgbW9uaXRvcmluZywgYW5kIG11bHRpcGxlIGRhdGEgbW92ZW1lbnRzIGJldHdlZW4gc3lzdGVtcy4gVGhpcyBpbmNyZWFzZXMgb3BlcmF0aW9uYWwgY29tcGxleGl0eSBhbmQgc2xvd3MgZG93biBkYXRhIGF2YWlsYWJpbGl0eS4NCg0KM++4j+KDoyBIaWdoIExhdGVuY3kgaW4gQW5hbHl0aWNzDQoNCkJ1c2luZXNzIHVzZXJzIGV4cGVjdCBuZWFyIHJlYWwtdGltZSBpbnNpZ2h0cywgYnV0IGJhdGNoLWhlYXZ5IGFyY2hpdGVjdHVyZXMgYW5kIHNlcXVlbnRpYWwgcHJvY2Vzc2luZyBjcmVhdGUgZGVsYXlzIGluIHJlcG9ydGluZyBhbmQgYW5hbHl0aWNzIGNvbnN1bXB0aW9uLg0KDQo077iP4oOjIERhdGEgRHVwbGljYXRpb24gJiBTdG9yYWdlIE92ZXJoZWFkDQoNClRvIHNoYXJlIGRhdGEgYWNyb3NzIHRlYW1zIG9yIHBhcnRuZXJzLCBvcmdhbml6YXRpb25zIG9mdGVuIHJlcGxpY2F0ZSBkYXRhc2V0cyBtdWx0aXBsZSB0aW1lcywgaW5jcmVhc2luZyBzdG9yYWdlIGNvc3RzIGFuZCBjcmVhdGluZyB2ZXJzaW9uLWNvbnRyb2wgY2hhbGxlbmdlcy4NCg0KNe+4j+KDoyBHb3Zlcm5hbmNlIGFuZCBTZWN1cml0eSBSaXNrcw0KDQpDcm9zcy10ZWFtIGFuZCBleHRlcm5hbCBkYXRhIHNoYXJpbmcgaW50cm9kdWNlcyByaXNrcyBhcm91bmQgdW5hdXRob3JpemVkIGFjY2VzcywgY29tcGxpYW5jZSB2aW9sYXRpb25zLCBhbmQgbGFjayBvZiBhdWRpdGFiaWxpdHkuDQoNCjbvuI/ig6MgTGltaXRlZCBTY2FsYWJpbGl0eQ0KDQpMZWdhY3kgYXJjaGl0ZWN0dXJlcyBzdHJ1Z2dsZSB0byBzY2FsZSB3aXRoIGdyb3dpbmcgZGF0YSB2b2x1bWVzLCBsZWFkaW5nIHRvIHBlcmZvcm1hbmNlIGJvdHRsZW5lY2tzIGFuZCB1bnByZWRpY3RhYmxlIGNvc3RzLg0KDQo377iP4oOjIExhY2sgb2YgQ29udHJvbGxlZCBEYXRhIFNoYXJpbmcgRnJhbWV3b3JrDQoNClRoZXJlIGlzIG5vIHN0YW5kYXJkaXplZCwgc2VjdXJlIG1lY2hhbmlzbSB0byBzaGFyZSBjdXJhdGVkIGRhdGEgaW50ZXJuYWxseSBvciBleHRlcm5hbGx5IHdpdGhvdXQgcGh5c2ljYWxseSBtb3ZpbmcgdGhlIGRhdGEuDQoNCkJ1c2luZXNzIENoYWxsZW5nZXMgaW4gRW50ZXJwcmlzZSBEYXRhIFNoYXJpbmcNCjHvuI/ig6MgTm8gU2luZ2xlIFZlcnNpb24gb2YgVHJ1dGgNCg0KRGlmZmVyZW50IGRlcGFydG1lbnRzIHJlbHkgb24gZGlmZmVyZW50IHN5c3RlbXMgYW5kIHJlcG9ydHMsIGxlYWRpbmcgdG8gaW5jb25zaXN0ZW50IG51bWJlcnMgaW4gbGVhZGVyc2hpcCBkaXNjdXNzaW9ucyBhbmQgcmVkdWNlZCB0cnVzdCBpbiBkYXRhLg0KDQoy77iP4oOjIERlbGF5ZWQgRGVjaXNpb24tTWFraW5nDQoNCkJ1c2luZXNzIGxlYWRlcnMgb2Z0ZW4gd2FpdCBob3VycyBvciBkYXlzIGZvciBjb25zb2xpZGF0ZWQgcmVwb3J0cywgaW1wYWN0aW5nIGFnaWxpdHkgaW4gcmVzcG9uZGluZyB0byBtYXJrZXQgYW5kIG9wZXJhdGlvbmFsIGNoYW5nZXMuDQoNCjPvuI/ig6MgSGlnaCBDb3N0IG9mIERhdGEgRHVwbGljYXRpb24NCg0KVG8gZW5hYmxlIGNvbGxhYm9yYXRpb24sIHRlYW1zIGZyZXF1ZW50bHkgY3JlYXRlIG11bHRpcGxlIGNvcGllcyBvZiB0aGUgc2FtZSBkYXRhLCBpbmNyZWFzaW5nIHN0b3JhZ2UgY29zdHMgYW5kIG9wZXJhdGlvbmFsIGluZWZmaWNpZW5jaWVzLg0KDQo077iP4oOjIExpbWl0ZWQgQ3Jvc3MtRnVuY3Rpb25hbCBDb2xsYWJvcmF0aW9uDQoNClNoYXJpbmcgZGF0YSBiZXR3ZWVuIGJ1c2luZXNzIHVuaXRzIG9yIHdpdGggZXh0ZXJuYWwgcGFydG5lcnMgaXMgc2xvdyBhbmQgY29tcGxleCwgcmVzdHJpY3RpbmcgaW5ub3ZhdGlvbiBhbmQgc3RyYXRlZ2ljIHBhcnRuZXJzaGlwcy4NCg0KNe+4j+KDoyBDb21wbGlhbmNlIGFuZCBSaXNrIEV4cG9zdXJlDQoNCldpdGhvdXQgYSBnb3Zlcm5lZCBzaGFyaW5nIGZyYW1ld29yaywgb3JnYW5pemF0aW9ucyBmYWNlIHJpc2tzIHJlbGF0ZWQgdG8gZGF0YSBwcml2YWN5LCByZWd1bGF0b3J5IGNvbXBsaWFuY2UsIGFuZCB1bmF1dGhvcml6ZWQgYWNjZXNzLg0KDQo277iP4oOjIFNjYWxpbmcgQ2hhbGxlbmdlcyB3aXRoIEJ1c2luZXNzIEdyb3d0aA0KDQpBcyBkYXRhIHZvbHVtZSBhbmQgYnVzaW5lc3Mgb3BlcmF0aW9ucyBncm93LCBleGlzdGluZyBwcm9jZXNzZXMgc3RydWdnbGUgdG8ga2VlcCB1cCwgbGVhZGluZyB0byBwZXJmb3JtYW5jZSBpc3N1ZXMgYW5kIGhpZ2hlciBtYWludGVuYW5jZSBjb3N0cy4NCg0KN++4j+KDoyBMYWNrIG9mIFJlYWwtVGltZSBCdXNpbmVzcyBWaXNpYmlsaXR5DQoNCkxlYWRlcnNoaXAgbGFja3MgdGltZWx5IGluc2lnaHRzIGludG8gS1BJcyBzdWNoIGFzIHJldmVudWUsIHV0aWxpemF0aW9uLCBpbnZlbnRvcnksIG9yIGN1c3RvbWVyIGJlaGF2aW9yLCBsaW1pdGluZyBwcm9hY3RpdmUgZGVjaXNpb24tbWFraW5nLg0KDQpTdGVwLWJ5LVN0ZXAgRmxvdw0KDQpEYXRhIGlzIHByb2R1Y2VkIGFjcm9zcyBidXNpbmVzcyBzeXN0ZW1zIChFUlAvU0FQLCBDUk0sIGRhdGFiYXNlcywgZmlsZXMsIHBhcnRuZXIgZmVlZHMsIElvVCwgZXRjLikuDQoNCkRhdGEgaXMgc2VjdXJlbHkgaW5nZXN0ZWQgaW50byBBV1MgdGhyb3VnaCBzdGFuZGFyZCBpbnRlcmZhY2VzIChBUElzLCBmaWxlIGRyb3BzLCBzY2hlZHVsZWQgZXh0cmFjdHMpLg0KDQpBbGwgaW5jb21pbmcgZGF0YSBsYW5kcyBpbiBhIGNlbnRyYWxpemVkIHN0b3JhZ2UgbGF5ZXIgKEFXUyBkYXRhIGxha2UpIHRvIGNyZWF0ZSBhIHNpbmdsZSwgdHJ1c3RlZCBpbnRha2UgcG9pbnQuDQoNCkF1dG9tYXRlZCB3b3JrZmxvd3MgdHJpZ2dlciBwcm9jZXNzaW5nIHdoZW4gbmV3IGRhdGEgYXJyaXZlcywgcmVkdWNpbmcgbWFudWFsIGludGVydmVudGlvbiBhbmQgZGVsYXlzLg0KDQpEYXRhIGlzIHN0YW5kYXJkaXplZCBhbmQgdmFsaWRhdGVkIChmb3JtYXQgY2hlY2tzLCBjb21wbGV0ZW5lc3MsIGJhc2ljIHF1YWxpdHkgcnVsZXMpIHRvIGltcHJvdmUgdHJ1c3QgYW5kIHVzYWJpbGl0eS4NCg0KQnVzaW5lc3MtcmVhZHkgY3VyYXRlZCBkYXRhc2V0cyBhcmUgY3JlYXRlZCAoY2xlYW5lZCwgc3RydWN0dXJlZCwgYW5kIG9yZ2FuaXplZCBmb3IgYW5hbHl0aWNzIHVzZSkuDQoNCkN1cmF0ZWQgZGF0YXNldHMgYXJlIGxvYWRlZCBpbnRvIFNub3dmbGFrZSB0byBzdXBwb3J0IGhpZ2gtcGVyZm9ybWFuY2UgYW5hbHl0aWNzIGFuZCBlbnRlcnByaXNlIHJlcG9ydGluZy4NCg0KU25vd2ZsYWtlIHRyYW5zZm9ybXMgZGF0YSBpbnRvIGNvbnN1bXB0aW9uIGxheWVycyAoc3ViamVjdCBhcmVhcywgcmVwb3J0aW5nIHRhYmxlcywgS1BJIHZpZXdzKSBhbGlnbmVkIHRvIGJ1c2luZXNzIG5lZWRzLg0KDQpBY2Nlc3MgaXMgZ292ZXJuZWQgdGhyb3VnaCByb2xlcyBhbmQgcG9saWNpZXMsIGVuc3VyaW5nIHRlYW1zIHNlZSBvbmx5IHdoYXQgdGhleSBhcmUgYWxsb3dlZCB0byBzZWUuDQoNCkRhdGEgaXMgc2hhcmVkIHNlY3VyZWx5ICh6ZXJvLWNvcHkpIHZpYSBTbm93Zmxha2UgYWNyb3NzIGludGVybmFsIGJ1c2luZXNzIHVuaXRzIG9yIGV4dGVybmFsIHBhcnRuZXJz4oCUd2l0aG91dCBkdXBsaWNhdGluZyBkYXRhc2V0cy4NCg0KVXNhZ2UgaXMgdHJhY2tlZCBhbmQgYXVkaXRhYmxlLCBlbmFibGluZyBjb21wbGlhbmNlIHJlcG9ydGluZyBhbmQgY29zdCB0cmFuc3BhcmVuY3kuDQoNCkNvbnRpbnVvdXMgbW9uaXRvcmluZyBhbmQgYWxlcnRzIGVuc3VyZSByZWxpYWJpbGl0eSwgZmFzdGVyIGlzc3VlIGRldGVjdGlvbiwgYW5kIHN0YWJsZSBidXNpbmVzcyBvcGVyYXRpb25zLg0KDQoNCkRhdGEgU2hhcmluZyBNb2RlbCDigJMgU2VjdXJlLCBaZXJvLUNvcHksIGFuZCBHb3Zlcm5lZA0K8J+OryBPYmplY3RpdmUNCg0KRW5hYmxlIHNlY3VyZSwgcmVhbC10aW1lIGRhdGEgY29sbGFib3JhdGlvbiBhY3Jvc3MgaW50ZXJuYWwgYnVzaW5lc3MgdW5pdHMgYW5kIGV4dGVybmFsIHBhcnRuZXJzIOKAlCB3aXRob3V0IGRhdGEgZHVwbGljYXRpb24gb3IgY29tcGxleCBpbnRlZ3JhdGlvbnMuDQoNCvCfj6IgMe+4j+KDoyBJbnRlcm5hbCBEYXRhIFNoYXJpbmcgKFdpdGhpbiBPcmdhbml6YXRpb24pDQoNCkNlbnRyYWxpemVkIGN1cmF0ZWQgZGF0YXNldHMgYXJlIHB1Ymxpc2hlZCBpbiBTbm93Zmxha2UNCg0KUm9sZS1iYXNlZCBhY2Nlc3MgZW5zdXJlcyBkZXBhcnRtZW50LWxldmVsIGNvbnRyb2wNCg0KRmluYW5jZSwgU2FsZXMsIE9wZXJhdGlvbnMgYWNjZXNzIHRoZSBzYW1lIHRydXN0ZWQgZGF0YQ0KDQpObyBkYXRhIHJlcGxpY2F0aW9uIGJldHdlZW4gdGVhbXMNCg0KTmVhciByZWFsLXRpbWUgdXBkYXRlcyBhdmFpbGFibGUgYXV0b21hdGljYWxseQ0KDQrwn5GJIE91dGNvbWU6IFNpbmdsZSBzb3VyY2Ugb2YgdHJ1dGggYWNyb3NzIHRoZSBlbnRlcnByaXNlDQoNCvCfpJ0gMu+4j+KDoyBFeHRlcm5hbCBEYXRhIFNoYXJpbmcgKFBhcnRuZXJzIC8gVmVuZG9ycyAvIENsaWVudHMpDQoNCkRhdGEgaXMgc2hhcmVkIHVzaW5nIFNub3dmbGFrZSBTZWN1cmUgRGF0YSBTaGFyaW5nDQoNClplcm8tY29weSBhcmNoaXRlY3R1cmUgKG5vIHBoeXNpY2FsIGRhdGEgbW92ZW1lbnQpDQoNCkNvbnRyb2xsZWQgYWNjZXNzIHRvIHNwZWNpZmljIHNjaGVtYXMgb3Igdmlld3MNCg0KUmVhbC10aW1lIGRhdGEgdXBkYXRlcyB3aXRob3V0IGZpbGUgZXhjaGFuZ2UNCg0KRnVsbCBhdWRpdCBhbmQgdXNhZ2UgdmlzaWJpbGl0eQ0KDQrwn5GJIE91dGNvbWU6IEZhc3RlciBjb2xsYWJvcmF0aW9uIHdpdGggcmVkdWNlZCBvcGVyYXRpb25hbCBvdmVyaGVhZA0KDQrwn5uhIDPvuI/ig6MgR292ZXJuYW5jZSAmIENvbnRyb2wgTGF5ZXINCg0KUm9sZS1CYXNlZCBBY2Nlc3MgQ29udHJvbCAoUkJBQykNCg0KRW5jcnlwdGlvbiBpbiB0cmFuc2l0ICYgYXQgcmVzdA0KDQpVc2FnZSBtb25pdG9yaW5nICYgYXVkaXQgdHJhY2tpbmcNCg0KRGF0YSBtYXNraW5nIC8gcm93LWxldmVsIHNlY3VyaXR5IChpZiByZXF1aXJlZCkNCg0KQ2VudHJhbGl6ZWQgcG9saWN5IGVuZm9yY2VtZW50DQoNCvCfkYkgT3V0Y29tZTogU2VjdXJlLCBjb21wbGlhbnQsIGVudGVycHJpc2UtZ3JhZGUgc2hhcmluZw0KDQrwn5KwIEJ1c2luZXNzIEltcGFjdA0KDQpFbGltaW5hdGVzIGR1cGxpY2F0ZSBzdG9yYWdlIGNvc3RzDQoNClJlZHVjZXMgbWFudWFsIGZpbGUgdHJhbnNmZXJzDQoNCkFjY2VsZXJhdGVzIHBhcnRuZXIgb25ib2FyZGluZw0KDQpJbXByb3ZlcyBkYXRhIHRydXN0ICYgdHJhbnNwYXJlbmN5DQoNClN1cHBvcnRzIHNjYWxhYmxlIGVudGVycHJpc2UgZ3Jvd3RoDQoNCkJ1c2luZXNzIEJlbmVmaXRzDQox77iP4oOjIEZhc3RlciBEZWNpc2lvbi1NYWtpbmcgd2l0aCBSZWFsLVRpbWUgSW5zaWdodHMNCg0KQnkgZW5hYmxpbmcgbmVhciByZWFsLXRpbWUgZGF0YSBhdmFpbGFiaWxpdHkgYW5kIGVsaW1pbmF0aW5nIG1hbnVhbCBkYXRhIGNvbnNvbGlkYXRpb24sIGxlYWRlcnNoaXAgZ2FpbnMgcXVpY2tlciBhY2Nlc3MgdG8gYWNjdXJhdGUgS1BJcy4NCg0KSW1wYWN0Og0KDQpSZWR1Y2VkIHJlcG9ydGluZyB0dXJuYXJvdW5kIHRpbWUNCg0KRmFzdGVyIHJlc3BvbnNlIHRvIG9wZXJhdGlvbmFsIGFuZCBtYXJrZXQgY2hhbmdlcw0KDQpJbXByb3ZlZCBleGVjdXRpdmUgY29uZmlkZW5jZSBpbiBkYXRhLWRyaXZlbiBkZWNpc2lvbnMNCg0KMu+4j+KDoyBTaW5nbGUgU291cmNlIG9mIFRydXRoIEFjcm9zcyB0aGUgRW50ZXJwcmlzZQ0KDQpDZW50cmFsaXplZCBpbmdlc3Rpb24gYW5kIGdvdmVybmVkIHNoYXJpbmcgZW5zdXJlIGFsbCBidXNpbmVzcyB1bml0cyBhY2Nlc3MgdGhlIHNhbWUgdHJ1c3RlZCBkYXRhc2V0cy4NCg0KSW1wYWN0Og0KDQpFbGltaW5hdGVzIGNvbmZsaWN0aW5nIHJlcG9ydHMNCg0KSW1wcm92ZXMgY3Jvc3MtZnVuY3Rpb25hbCBhbGlnbm1lbnQNCg0KSW5jcmVhc2VzIGRhdGEgdHJ1c3QgYWNyb3NzIGxlYWRlcnNoaXAgdGVhbXMNCg0KM++4j+KDoyBSZWR1Y2VkIE9wZXJhdGlvbmFsIE92ZXJoZWFkDQoNCkF1dG9tYXRpb24gdGhyb3VnaCBBV1Mgd29ya2Zsb3dzIGFuZCBTbm93Zmxha2UgZWxpbWluYXRlcyBtYW51YWwgZmlsZSB0cmFuc2ZlcnMsIHJlcGV0aXRpdmUgRVRMIHByb2Nlc3NlcywgYW5kIHJlY29uY2lsaWF0aW9uIGVmZm9ydHMuDQoNCkltcGFjdDoNCg0KTG93ZXIgZGVwZW5kZW5jeSBvbiBtYW51YWwgaW50ZXJ2ZW50aW9ucw0KDQpSZWR1Y2VkIElUIHN1cHBvcnQgd29ya2xvYWQNCg0KSW5jcmVhc2VkIHRlYW0gcHJvZHVjdGl2aXR5DQoNCjTvuI/ig6MgQ29zdCBPcHRpbWl6YXRpb24NCg0KWmVyby1jb3B5IGRhdGEgc2hhcmluZyByZW1vdmVzIHRoZSBuZWVkIGZvciBkYXRhc2V0IGR1cGxpY2F0aW9uLiBBV1Mgc2VydmVybGVzcyBzZXJ2aWNlcyBhbmQgU25vd2ZsYWtl4oCZcyBzY2FsYWJsZSBjb21wdXRlIG1vZGVsIG9wdGltaXplIGluZnJhc3RydWN0dXJlIGNvc3RzLg0KDQpJbXBhY3Q6DQoNCkxvd2VyIHN0b3JhZ2UgY29zdHMNCg0KUGF5LWZvci13aGF0LXlvdS11c2UgY29tcHV0ZSBtb2RlbA0KDQpCZXR0ZXIgY29zdCB2aXNpYmlsaXR5IGFuZCBwcmVkaWN0YWJpbGl0eQ0KDQo177iP4oOjIFNlY3VyZSBhbmQgQ29tcGxpYW50IERhdGEgQ29sbGFib3JhdGlvbg0KDQpCdWlsdC1pbiBnb3Zlcm5hbmNlLCBSQkFDLCBlbmNyeXB0aW9uLCBhbmQgYXVkaXQgdHJhY2tpbmcgcmVkdWNlIGNvbXBsaWFuY2Ugcmlza3Mgd2hpbGUgZW5hYmxpbmcgc2VjdXJlIGludGVybmFsIGFuZCBleHRlcm5hbCBzaGFyaW5nLg0KDQpJbXBhY3Q6DQoNClJlZHVjZWQgcmVndWxhdG9yeSBleHBvc3VyZQ0KDQpDb250cm9sbGVkIHBhcnRuZXIgYWNjZXNzDQoNCkZ1bGwgYXVkaXQgdHJhbnNwYXJlbmN5DQoNCjbvuI/ig6MgU2NhbGFibGUgZm9yIEJ1c2luZXNzIEdyb3d0aA0KDQpUaGUgYXJjaGl0ZWN0dXJlIGlzIGNsb3VkLW5hdGl2ZSBhbmQgZWxhc3RpYywgYWxsb3dpbmcgdGhlIG9yZ2FuaXphdGlvbiB0byBoYW5kbGUgaW5jcmVhc2luZyBkYXRhIHZvbHVtZXMgYW5kIG5ldyBidXNpbmVzcyB1c2UgY2FzZXMgd2l0aG91dCByZWRlc2lnbi4NCg0KSW1wYWN0Og0KDQpTdXBwb3J0cyBleHBhbnNpb24gaW50byBuZXcgbWFya2V0cw0KDQpFYXNpbHkgb25ib2FyZCBuZXcgcGFydG5lcnMNCg0KRnV0dXJlLXJlYWR5IGRhdGEgcGxhdGZvcm0NCg0KN++4j+KDoyBBY2NlbGVyYXRlZCBQYXJ0bmVyICYgRWNvc3lzdGVtIEVuYWJsZW1lbnQNCg0KU2VjdXJlIGRhdGEgc2hhcmluZyBhbGxvd3MgZXh0ZXJuYWwgc3Rha2Vob2xkZXJzICh2ZW5kb3JzLCBkaXN0cmlidXRvcnMsIGNsaWVudHMpIHRvIGFjY2VzcyBjdXJhdGVkIGRhdGEgaW5zdGFudGx5IHdpdGhvdXQgY29tcGxleCBpbnRlZ3JhdGlvbiBwcm9qZWN0cy4NCg0KSW1wYWN0Og0KDQpGYXN0ZXIgcGFydG5lciBvbmJvYXJkaW5nDQoNCkltcHJvdmVkIHN1cHBseSBjaGFpbiBjb2xsYWJvcmF0aW9uDQoNCkVuaGFuY2VkIGN1c3RvbWVyIGV4cGVyaWVuY2UNCg0KOO+4j+KDoyBJbXByb3ZlZCBEYXRhIEdvdmVybmFuY2UgJiBUcmFuc3BhcmVuY3kNCg0KQ2VudHJhbCBtb25pdG9yaW5nIGFuZCBwb2xpY3ktYmFzZWQgYWNjZXNzIGVuc3VyZSBjbGVhciB2aXNpYmlsaXR5IGludG8gd2hvIGlzIGFjY2Vzc2luZyB3aGF0IGRhdGEgYW5kIHdoZW4uDQoNCkltcGFjdDoNCg0KU3Ryb25nZXIgYWNjb3VudGFiaWxpdHkNCg0KQmV0dGVyIGF1ZGl0IHJlYWRpbmVzcw0KDQpJbmNyZWFzZWQgb3JnYW5pemF0aW9uYWwgZGF0YSBtYXR1cml0eQ0KDQrwn46vIEV4ZWN1dGl2ZSBTdW1tYXJ5IExpbmUgKEZvciBTbGlkZSBGb290ZXIpDQoNClRoaXMgc29sdXRpb24gdHJhbnNmb3JtcyBkYXRhIHNoYXJpbmcgZnJvbSBhIG1hbnVhbCwgc2lsb2VkIHByb2Nlc3MgaW50byBhIHNlY3VyZSwgc2NhbGFibGUsIGFuZCBjb3N0LWVmZmljaWVudCBlbnRlcnByaXNlIGNhcGFiaWxpdHkuDQoNCklmIHlvdSdkIGxpa2UsIEkgY2FuIG5leHQ6DQoNCkNvbnZlcnQgdGhpcyBpbnRvIHF1YW50aWZpYWJsZSBtZXRyaWNzIHN0eWxlIChlLmcuLCAzMOKAkzQwJSBjb3N0IHJlZHVjdGlvbiB0eXBlIHBvc2l0aW9uaW5nKSwNCg0KT3IgbWFrZSBpdCBtb3JlIENYTy1sZXZlbCBjcmlzcCAoc2hvcnQgJiBwb3dlcmZ1bCkgZm9yIGZpbmFsIHByZXNlbnRhdGlvbi4="
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client.kubernetes_cost_optimizer

# LLM Integration
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
    if not emergent_llm_key:
        print("Warning: EMERGENT_LLM_KEY not found in environment variables")
except ImportError:
    print("Warning: emergentintegrations not installed")
    LlmChat = None
    UserMessage = None

# Pydantic Models
class ClusterNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    cpu_capacity: float
    memory_capacity: float
    cpu_usage: float
    memory_usage: float
    cost_per_hour: float
    node_type: str
    zone: str
    status: str

class ClusterInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    provider: str
    region: str
    nodes: List[ClusterNode]
    total_cost: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CostAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    analysis_type: str
    recommendations: List[str]
    potential_savings: float
    confidence_score: float
    ai_insights: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OptimizationRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    type: str
    description: str
    impact: str
    savings_estimate: float
    implementation_complexity: str
    priority: str

class AnomalyAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_id: str
    alert_type: str
    description: str
    severity: str
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False

# AI Chat Service
class AIAnalysisService:
    def __init__(self):
        self.llm_chat = None
        if LlmChat and emergent_llm_key:
            self.llm_chat = LlmChat(
                api_key=emergent_llm_key,
                session_id="k8s-cost-optimizer",
                system_message="You are an expert Kubernetes cost optimization analyst. Provide detailed, actionable insights about cluster costs, resource utilization, and optimization opportunities. Always include specific recommendations and estimated savings."
            ).with_model("openai", "gpt-4o")
    
    async def analyze_cluster_costs(self, cluster: ClusterInfo) -> str:
        if not self.llm_chat:
            return "AI analysis unavailable - LLM integration not configured"
        
        cluster_data = {
            "name": cluster.name,
            "provider": cluster.provider,
            "total_cost": cluster.total_cost,
            "node_count": len(cluster.nodes),
            "total_cpu_capacity": sum(node.cpu_capacity for node in cluster.nodes),
            "total_memory_capacity": sum(node.memory_capacity for node in cluster.nodes),
            "avg_cpu_utilization": sum(node.cpu_usage for node in cluster.nodes) / len(cluster.nodes) if cluster.nodes else 0,
            "avg_memory_utilization": sum(node.memory_usage for node in cluster.nodes) / len(cluster.nodes) if cluster.nodes else 0
        }
        
        prompt = f"""
        Analyze this Kubernetes cluster for cost optimization opportunities:
        
        Cluster: {cluster_data['name']} ({cluster_data['provider']})
        Monthly Cost: ${cluster_data['total_cost']:.2f}
        Nodes: {cluster_data['node_count']}
        Total CPU: {cluster_data['total_cpu_capacity']} cores
        Total Memory: {cluster_data['total_memory_capacity']} GB
        Avg CPU Utilization: {cluster_data['avg_cpu_utilization']:.1f}%
        Avg Memory Utilization: {cluster_data['avg_memory_utilization']:.1f}%
        
        Provide a comprehensive cost analysis including:
        1. Current cost efficiency assessment
        2. Resource utilization insights
        3. Specific optimization recommendations
        4. Estimated potential savings
        5. Priority action items
        """
        
        try:
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            return response
        except Exception as e:
            return f"AI analysis error: {str(e)}"
    
    async def generate_recommendations(self, cluster: ClusterInfo) -> List[str]:
        if not self.llm_chat:
            return [
                "Enable cluster autoscaling to optimize node count",
                "Review resource requests and limits for over-provisioning",
                "Consider spot/preemptible instances for non-critical workloads"
            ]
        
        prompt = f"""
        Generate 5 specific, actionable optimization recommendations for this Kubernetes cluster:
        
        Cluster: {cluster.name}
        Provider: {cluster.provider}
        Current monthly cost: ${cluster.total_cost}
        Nodes: {len(cluster.nodes)}
        
        Focus on recommendations that can provide immediate cost savings while maintaining performance.
        Return only the recommendations as a numbered list.
        """
        
        try:
            user_message = UserMessage(text=prompt)
            response = await self.llm_chat.send_message(user_message)
            # Parse recommendations from response
            recommendations = [line.strip() for line in response.split('\
') if line.strip() and any(char.isdigit() for char in line[:3])]
            return recommendations[:5] if recommendations else [
                "Enable horizontal pod autoscaling for better resource utilization",
                "Implement resource quotas to prevent over-provisioning",
                "Use node affinity rules to optimize workload placement",
                "Consider reserved instances for predictable workloads",
                "Implement pod disruption budgets for safer scaling"
            ]
        except Exception as e:
            return [f"AI recommendation error: {str(e)}"]

ai_service = AIAnalysisService()

# Mock data generators
def generate_mock_cluster_nodes(count: int = 5) -> List[ClusterNode]:
    node_types = ["t3.medium", "t3.large", "t3.xlarge", "m5.large", "m5.xlarge"]
    zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
    
    nodes = []
    for i in range(count):
        node_type = random.choice(node_types)
        cpu_capacity = {"t3.medium": 2, "t3.large": 2, "t3.xlarge": 4, "m5.large": 2, "m5.xlarge": 4}[node_type]
        memory_capacity = {"t3.medium": 4, "t3.large": 8, "t3.xlarge": 16, "m5.large": 8, "m5.xlarge": 16}[node_type]
        cost_per_hour = {"t3.medium": 0.0416, "t3.large": 0.0832, "t3.xlarge": 0.1664, "m5.large": 0.096, "m5.xlarge": 0.192}[node_type]
        
        nodes.append(ClusterNode(
            name=f"node-{i+1}",
            cpu_capacity=cpu_capacity,
            memory_capacity=memory_capacity,
            cpu_usage=random.uniform(20, 80),
            memory_usage=random.uniform(30, 85),
            cost_per_hour=cost_per_hour,
            node_type=node_type,
            zone=random.choice(zones),
            status="Ready"
        ))
    
    return nodes

def generate_mock_clusters(count: int = 3) -> List[ClusterInfo]:
    providers = ["AWS", "GCP", "Azure"]
    regions = ["us-east-1", "us-west-2", "europe-west1"]
    
    clusters = []
    for i in range(count):
        nodes = generate_mock_cluster_nodes(random.randint(3, 8))
        total_cost = sum(node.cost_per_hour * 24 * 30 for node in nodes)  # Monthly cost
        
        clusters.append(ClusterInfo(
            name=f"production-cluster-{i+1}",
            provider=random.choice(providers),
            region=random.choice(regions),
            nodes=nodes,
            total_cost=total_cost
        ))
    
    return clusters

# API Endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Kubernetes Cost Optimizer API is running"}

@app.get("/api/clusters", response_model=List[ClusterInfo])
async def get_clusters():
    """Get all Kubernetes clusters with cost information"""
    try:
        clusters = await db.clusters.find().to_list(length=None)
        if not clusters:
            # Generate and store mock data
            mock_clusters = generate_mock_clusters()
            for cluster_data in mock_clusters:
                cluster_dict = cluster_data.dict()
                cluster_dict['created_at'] = cluster_dict['created_at'].isoformat()
                for node in cluster_dict['nodes']:
                    node['id'] = node.get('id', str(uuid.uuid4()))
                await db.clusters.insert_one(cluster_dict)
            clusters = await db.clusters.find().to_list(length=None)
        
        return [ClusterInfo(**cluster) for cluster in clusters]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching clusters: {str(e)}")

@app.get("/api/clusters/{cluster_id}", response_model=ClusterInfo)
async def get_cluster(cluster_id: str):
    """Get detailed information about a specific cluster"""
    cluster = await db.clusters.find_one({"id": cluster_id})
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return ClusterInfo(**cluster)

@app.post("/api/clusters/{cluster_id}/analyze")
async def analyze_cluster(cluster_id: str):
    """Generate AI-powered cost analysis for a cluster"""
    cluster = await db.clusters.find_one({"id": cluster_id})
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    cluster_obj = ClusterInfo(**cluster)
    
    # Generate AI analysis
    ai_insights = await ai_service.analyze_cluster_costs(cluster_obj)
    recommendations = await ai_service.generate_recommendations(cluster_obj)
    
    # Calculate potential savings (mock calculation)
    current_utilization = sum(node['cpu_usage'] for node in cluster['nodes']) / len(cluster['nodes'])
    potential_savings = cluster_obj.total_cost * (100 - current_utilization) / 100 * 0.3
    
    analysis = CostAnalysis(
        cluster_id=cluster_id,
        analysis_type="comprehensive",
        recommendations=recommendations,
        potential_savings=potential_savings,
        confidence_score=random.uniform(85, 95),
        ai_insights=ai_insights
    )
    
    # Store analysis
    analysis_dict = analysis.dict()
    analysis_dict['created_at'] = analysis_dict['created_at'].isoformat()
    await db.cost_analyses.insert_one(analysis_dict)
    
    return analysis

@app.get("/api/clusters/{cluster_id}/recommendations", response_model=List[OptimizationRecommendation])
async def get_recommendations(cluster_id: str):
    """Get optimization recommendations for a cluster"""
    cluster = await db.clusters.find_one({"id": cluster_id})
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Generate mock recommendations
    recommendations = [
        OptimizationRecommendation(
            cluster_id=cluster_id,
            type="rightsizing",
            description="Downsize over-provisioned nodes in zone us-east-1a",
            impact="Reduce costs by optimizing node sizes",
            savings_estimate=450.00,
            implementation_complexity="Medium",
            priority="High"
        ),
        OptimizationRecommendation(
            cluster_id=cluster_id,
            type="scaling",
            description="Enable cluster autoscaling to handle traffic spikes",
            impact="Automatically adjust cluster size based on demand",
            savings_estimate=320.00,
            implementation_complexity="Low",
            priority="High"
        ),
        OptimizationRecommendation(
            cluster_id=cluster_id,
            type="scheduling",
            description="Implement pod affinity rules for better resource utilization",
            impact="Improve workload distribution across nodes",
            savings_estimate=180.00,
            implementation_complexity="High",
            priority="Medium"
        )
    ]
    
    return recommendations

@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get dashboard overview with key metrics"""
    clusters = await db.clusters.find().to_list(length=None)
    
    if not clusters:
        clusters = [cluster.dict() for cluster in generate_mock_clusters()]
    
    total_clusters = len(clusters)
    total_cost = sum(cluster.get('total_cost', 0) for cluster in clusters)
    total_nodes = sum(len(cluster.get('nodes', [])) for cluster in clusters)
    
    # Calculate average utilization
    all_nodes = []
    for cluster in clusters:
        all_nodes.extend(cluster.get('nodes', []))
    
    avg_cpu_utilization = sum(node.get('cpu_usage', 0) for node in all_nodes) / len(all_nodes) if all_nodes else 0
    avg_memory_utilization = sum(node.get('memory_usage', 0) for node in all_nodes) / len(all_nodes) if all_nodes else 0
    
    # Mock cost trends (last 7 days)
    cost_trends = []
    base_cost = total_cost / 30  # Daily cost
    for i in range(7):
        date = (datetime.now(timezone.utc) - timedelta(days=6-i)).date()
        daily_cost = base_cost * random.uniform(0.9, 1.1)
        cost_trends.append({
            "date": date.isoformat(),
            "cost": round(daily_cost, 2)
        })
    
    return {
        "total_clusters": total_clusters,
        "total_monthly_cost": round(total_cost, 2),
        "total_nodes": total_nodes,
        "avg_cpu_utilization": round(avg_cpu_utilization, 1),
        "avg_memory_utilization": round(avg_memory_utilization, 1),
        "cost_trends": cost_trends,
        "potential_savings": round(total_cost * 0.25, 2),  # Mock 25% potential savings
        "alerts_count": random.randint(2, 8)
    }

@app.get("/api/alerts", response_model=List[AnomalyAlert])
async def get_alerts():
    """Get cost anomaly alerts"""
    alerts = await db.alerts.find().to_list(length=None)
    
    if not alerts:
        # Generate mock alerts
        clusters = await db.clusters.find().to_list(length=None)
        if clusters:
            mock_alerts = []
            for i in range(random.randint(3, 6)):
                cluster = random.choice(clusters)
                alert = AnomalyAlert(
                    cluster_id=cluster['id'],
                    alert_type=random.choice(["cost_spike", "resource_waste", "scaling_issue"]),
                    description=f"Unusual cost pattern detected in {cluster['name']}",
                    severity=random.choice(["low", "medium", "high"])
                )
                mock_alerts.append(alert)
            
            # Store alerts
            for alert in mock_alerts:
                alert_dict = alert.dict()
                alert_dict['detected_at'] = alert_dict['detected_at'].isoformat()
                await db.alerts.insert_one(alert_dict)
            
            alerts = await db.alerts.find().to_list(length=None)
    
    return [AnomalyAlert(**alert) for alert in alerts]

@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved"""
    result = await db.alerts.update_one(
        {"id": alert_id},
        {"$set": {"resolved": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert resolved successfully"}

@app.get("/api/cost-analysis")
async def get_cost_analysis():
    """Get comprehensive cost analysis across all clusters"""
    analyses = await db.cost_analyses.find().to_list(length=None)
    return [CostAnalysis(**analysis) for analysis in analyses]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
